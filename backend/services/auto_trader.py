"""
Real-Time Automated Trading Service
Monitors enabled symbols and executes trades based on Renko brick color changes
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import MetaTrader5 as mt5

from backend.renko.engine import RenkoEngine
from backend.strategy.engine import StrategyEngine
from backend.mt5.connection import mt5_manager
from backend.config import settings
import httpx

logger = logging.getLogger(__name__)

class AutoTrader:
    """Background service for automated trading based on Renko strategy"""
    
    def __init__(self):
        self.enabled_symbols: Dict[str, dict] = {}  # {symbol: {account_id, enabled, brick_size, ...}}
        self.renko_engines: Dict[str, RenkoEngine] = {}
        self.strategy_engines: Dict[str, StrategyEngine] = {}
        self.last_brick_state: Dict[str, str] = {}  # {symbol_key: 'green'/'red'} track last color
        self.last_candle_times: Dict[str, int] = {}  # {engine_key: unix_ts} only feed NEW candles
        self.last_trade_time: Dict[str, float] = {}  # {symbol_key: epoch} cooldown per symbol
        self.open_positions: Dict[str, dict] = {}  # {symbol: {ticket, direction, entry_price, ...}}
        # Pending 1-minute confirmation state per symbol
        # {symbol_key: {direction, limit_price, start_time, violated, order_placed, order_ticket}}
        self.pending_signals: Dict[str, dict] = {}
        self.is_running = False
        self.supabase_client = None
        
    async def initialize(self):
        """Initialize auto-trader service"""
        try:
            logger.info("🤖 Initializing Auto-Trader Service...")
            
            # Use shared service-role client (bypasses RLS)
            from backend.supabase.client import supabase_client as _shared_client
            self.supabase_client = _shared_client
            
            # Load enabled symbols from database
            await self.load_watchlist()
            
            logger.info(f"✅ Auto-Trader initialized with {len(self.enabled_symbols)} symbols")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Auto-Trader: {e}")
    
    def calculate_lot_size(self, balance: float) -> float:
        """Calculate lot size based on account balance
        
        Rules:
        - $0-$1000: 0.01 lot
        - $1001-$10000: 0.1 lot
        - $10001-$25000: 1.0 lot
        - $25001+: 1.0 lot (max)
        """
        if balance <= 1000:
            return 0.01
        elif balance <= 10000:
            return 0.1
        else:
            return 1.0
    
    async def load_watchlist(self):
        """Load auto-trading watchlist from Supabase for ACTIVE accounts only"""
        try:
            if not self.supabase_client:
                logger.warning("Supabase client not initialized")
                return
            
            # Get active account logins so we skip disconnected accounts
            active_accounts_res = self.supabase_client.table('accounts').select('login').neq('status', 'inactive').execute()
            active_logins = {str(row['login']) for row in (active_accounts_res.data or [])}
            logger.info(f"📋 Active accounts in DB: {active_logins or '(none)'}")

            # Also accept accounts connected in mt5_manager even if not in DB
            for login in mt5_manager.sessions:
                active_logins.add(str(login))
            logger.info(f"📋 Active accounts (DB + MT5 manager): {active_logins or '(none)'}")
            
            # Fetch all active symbols across all accounts
            # Use is_active=True as primary filter; algo_enabled=False means user disabled trading for that symbol
            response = self.supabase_client.table('watchlist').select('*').neq('is_active', False).execute()
            logger.info(f"📋 Watchlist rows with is_active=True: {len(response.data) if response.data else 0}")
            for item in (response.data or []):
                logger.info(f"   Row: symbol={item.get('symbol')} account_id={item.get('account_id')} algo_enabled={item.get('algo_enabled')} is_active={item.get('is_active')}")
            
            # Group by account_id to track accounts and their enabled symbols
            accounts_symbols = {}
            
            for item in (response.data or []):
                symbol = item['symbol']
                account_id = item['account_id']
                
                # Skip if user explicitly disabled algo trading (null/missing = enabled by default)
                algo_enabled = item.get('algo_enabled')
                if algo_enabled is False:
                    logger.info(f"   Skipping {symbol} (account {account_id}) — algo_enabled is False")
                    continue
                
                # Skip symbols belonging to inactive/disconnected accounts
                if str(account_id) not in active_logins:
                    logger.warning(
                        f"⚠️ Skipping {symbol} (account_id={account_id}) — not in active_logins {active_logins}. "
                        f"Add account to MT5 or mark as active in Supabase."
                    )
                    continue
                
                # Create key combining account and symbol for unique tracking
                symbol_key = f"{account_id}_{symbol}"
                new_brick_size = item.get('brick_size', 1.0)
                
                # If brick_size changed, clear the old engine so it reinitializes
                old_config = self.enabled_symbols.get(symbol_key)
                if old_config and old_config.get('brick_size') != new_brick_size:
                    old_key = f"{account_id}_{symbol}_{old_config['brick_size']}"
                    self.renko_engines.pop(old_key, None)
                    self.strategy_engines.pop(old_key, None)
                    self.last_candle_times.pop(old_key, None)
                    self.last_brick_state.pop(symbol_key, None)
                    self.pending_signals.pop(symbol_key, None)
                    logger.info(f"🔄 Brick size changed for {symbol}: {old_config['brick_size']} -> {new_brick_size}, engine reset")
                
                self.enabled_symbols[symbol_key] = {
                    'symbol': symbol,
                    'account_id': account_id,
                    'algo_enabled': True,
                    'lot_size': item.get('lot_size', 0.01),
                    'brick_size': new_brick_size,
                    'use_trailing_stop': item.get('use_trailing_stop', False),
                    'stop_loss_pips': item.get('stop_loss_pips', 50),
                    'take_profit_pips': item.get('take_profit_pips', 100),
                    'created_at': item.get('created_at'),
                }
                
                # Track accounts
                if account_id not in accounts_symbols:
                    accounts_symbols[account_id] = []
                accounts_symbols[account_id].append(symbol)
            
            logger.info(f"📋 Loaded {len(self.enabled_symbols)} symbol/account pairs from watchlist")
            for account_id, symbols in accounts_symbols.items():
                logger.info(f"   Account {account_id}: {', '.join(symbols)}")
        
        except Exception as e:
            logger.error(f"❌ Failed to load watchlist: {e}")
    
    async def start(self):
        """Start the auto-trading service (background loop)"""
        if self.is_running:
            logger.warning("Auto-Trader already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting Auto-Trader service...")

        # Wait for MT5 to finish connecting before first evaluation.
        # MT5 connects in a background thread at startup — this prevents
        # the first N evaluations from all failing with 'not connected'.
        await asyncio.sleep(8)

        reload_counter = 0
        while self.is_running:
            try:
                # Reload watchlist every 30 seconds to pick up new symbols added from UI
                if reload_counter % 30 == 0:
                    await self.load_watchlist()
                
                await self.evaluate_strategy()
            except Exception as e:
                # IMPORTANT: log and continue — never let a single exception kill the loop.
                # Previously the loop exited here which stopped all trading permanently.
                logger.error(f"❌ Auto-Trader loop error (continuing): {e}", exc_info=True)
            
            await asyncio.sleep(1)
            reload_counter += 1

        logger.info("⏹️ Auto-Trader loop exited")
    
    async def stop(self):
        """Stop the auto-trading service"""
        logger.info("⏹️ Stopping Auto-Trader service...")
        self.is_running = False
    
    async def evaluate_strategy(self):
        """Evaluate strategy for all symbols - runs sync MT5 work in thread to avoid blocking event loop"""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._collect_signals_sync)
            self._last_evaluation_time = datetime.now()
            for result in results:
                # Limit order was already placed inside _check_signal_sync; just log it
                await self.log_trade(
                    result['symbol'], result['signal'],
                    result['entry_price'], result['lot_size'], result['account_id']
                )
        except Exception as e:
            logger.error(f"❌ Strategy evaluation error: {e}")

    def _collect_signals_sync(self) -> list:
        """Synchronous signal collection - runs in thread pool.
        Groups symbols by account to minimize mt5.login() calls (one per account switch).
        Returns list of {symbol, signal, entry_price, lot_size, account_id} dicts (limit orders placed).
        """
        signals = []

        # Group by account_id to call switch_to() once per account
        by_account: Dict[int, list] = {}
        for symbol_key, config in list(self.enabled_symbols.items()):
            if not config.get('algo_enabled', False):
                continue
            account_id = config['account_id']
            if account_id not in by_account:
                by_account[account_id] = []
            by_account[account_id].append((symbol_key, config))

        for account_id, items in by_account.items():
            session = mt5_manager.get_session(account_id)
            if not session:
                logger.warning(f"⚠️ Account {account_id} not found in manager")
                continue
            try:
                session.switch_to()
            except Exception as e:
                logger.warning(f"⚠️ Account {account_id} switch failed: {e} — attempting reconnect")
                try:
                    session.connect(max_retries=1)
                    session.switch_to()
                    logger.info(f"✅ Account {account_id} reconnected successfully")
                except Exception as e2:
                    logger.error(f"❌ Account {account_id} reconnect failed: {e2} — skipping")
                    continue
            if not session.connected:
                continue

            for symbol_key, config in items:
                try:
                    sig = self._check_signal_sync(symbol_key, config, account_id)
                    if sig:
                        signals.append(sig)
                except Exception as e:
                    logger.error(f"❌ Error checking signal for {symbol_key}: {e}")

        return signals

    def _check_signal_sync(self, symbol_key: str, config: dict, account_id: int) -> Optional[dict]:
        """
        Renko + 1-minute confirmation strategy:
        - Green brick after red(s): if price stays ABOVE brick close for 60s → BUY LIMIT at brick close
        - Red brick after green(s): cancel pending BUY LIMIT; if price stays BELOW brick close 60s → SELL LIMIT at brick close
        Returns a result dict when a limit order is placed, else None.
        """
        symbol = config['symbol']
        brick_size = config.get('brick_size', 1.0)

        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
        if rates is None or len(rates) == 0:
            logger.debug(f"⏳ No rate data yet for {symbol}")
            return None

        engine_key = f"{account_id}_{symbol}_{brick_size}"
        if engine_key not in self.renko_engines:
            logger.info(f"🏗️ Creating Renko engine for {symbol} with brick_size={brick_size}")
            self.renko_engines[engine_key] = RenkoEngine(brick_size)
            self.strategy_engines[engine_key] = StrategyEngine(self.renko_engines[engine_key])

        renko = self.renko_engines[engine_key]

        rates_sorted = sorted(rates, key=lambda r: int(r['time']))
        last_fed_time = self.last_candle_times.get(engine_key, 0)
        if last_fed_time == 0:
            new_rates = rates_sorted
            logger.info(f"📊 Initializing Renko engine for {symbol} with {len(new_rates)} historical candles")
        else:
            new_rates = [r for r in rates_sorted if int(r['time']) > last_fed_time]

        if new_rates:
            for rate in new_rates:
                renko.feed_tick(rate['close'], int(rate['time']))
            self.last_candle_times[engine_key] = max(int(r['time']) for r in new_rates)

        all_bricks = renko.bricks  # full history needed to find first brick of new color
        if len(all_bricks) == 0:
            logger.info(f"⏳ [{symbol}] No bricks yet (brick_size={brick_size})")
            return None

        current_brick = all_bricks[-1]
        current_color = current_brick.color
        last_color = self.last_brick_state.get(symbol_key)

        if last_color is None:
            if len(all_bricks) >= 2:
                last_color = all_bricks[-2].color
                logger.info(f"📊 [{symbol}] Initialized: prev={last_color}, current={current_color}")
            else:
                self.last_brick_state[symbol_key] = current_color
                return None

        # Get live bid price for confirmation checks
        tick = mt5.symbol_info_tick(symbol)
        current_price = float(tick.bid) if tick else None

        # ── BRICK CHANGE: new brick formed ────────────────────────────────────
        if last_color != current_color:
            new_direction = 'BUY' if current_color == 'green' else 'SELL'
            first_new_idx = len(all_bricks) - 1
            while first_new_idx > 0 and all_bricks[first_new_idx - 1].color == current_color:
                first_new_idx -= 1
            first_brick = all_bricks[first_new_idx]
            limit_price = first_brick.close_price  # close of first new-direction brick

            # Cancel any existing pending limit order for this symbol
            existing = self.pending_signals.get(symbol_key, {})
            if existing.get('order_ticket'):
                self._cancel_pending_order_sync(symbol, account_id, existing['order_ticket'])

            # Close any open position in the opposite direction
            self._close_opposite_position_sync(symbol, account_id)

            # Start new 60-second confirmation window
            self.pending_signals[symbol_key] = {
                'direction': new_direction,
                'limit_price': limit_price,
                'start_time': float(first_brick.timestamp) if first_brick.timestamp else time.time(),
                'violated': False,
                'order_placed': False,
                'order_ticket': None,
            }
            logger.info(
                f"📊 [{symbol}] Brick: {last_color}→{current_color} | "
                f"Waiting 60s confirmation for {new_direction} LIMIT @ {limit_price}"
            )

        self.last_brick_state[symbol_key] = current_color

        # ── CONFIRMATION CHECK ─────────────────────────────────────────────────
        pending = self.pending_signals.get(symbol_key)
        if not pending or pending.get('order_placed') or pending.get('violated'):
            return None
        if current_price is None:
            return None

        direction = pending['direction']
        limit_price = pending['limit_price']
        elapsed = time.time() - pending['start_time']

        # If price crossed to the wrong side during the confirmation window → abort
        if direction == 'BUY' and current_price < limit_price:
            pending['violated'] = True
            logger.info(f"⚠️ [{symbol}] BUY confirmation cancelled: price {current_price} dropped below {limit_price}")
            return None
        if direction == 'SELL' and current_price > limit_price:
            pending['violated'] = True
            logger.info(f"⚠️ [{symbol}] SELL confirmation cancelled: price {current_price} rose above {limit_price}")
            return None

        # Place limit order after 60 seconds of uninterrupted confirmation
        if elapsed >= 60.0:
            logger.info(f"✅ [{symbol}] {direction} confirmed (60s). Placing LIMIT @ {limit_price}")
            result = self._place_limit_order_sync(symbol, direction, limit_price, account_id, config)
            if result:
                pending['order_placed'] = True
                pending['order_ticket'] = result['ticket']
                return {
                    'symbol': symbol,
                    'signal': direction,
                    'account_id': account_id,
                    'entry_price': limit_price,
                    'lot_size': result['lot_size'],
                }

        return None

    async def evaluate_symbol(self, symbol_key: str):
        """Legacy single-symbol evaluator - kept for compatibility. Prefer _collect_signals_sync."""
        config = self.enabled_symbols.get(symbol_key)
        if not config or not config.get('algo_enabled', False):
            return
        account_id = config['account_id']
        session = mt5_manager.get_session(account_id)
        if not session:
            return
        try:
            session.switch_to()
        except Exception as e:
            logger.warning(f"⚠️ {account_id} switch failed: {e}")
            return
        result = self._check_signal_sync(symbol_key, config, account_id)
        if result:
            await self.log_trade(result['symbol'], result['signal'], result['entry_price'], result['lot_size'], result['account_id'])
    
    async def execute_trade(self, symbol: str, signal: str, account_id: int, config: dict):
        """Execute a trade based on signal - runs sync MT5 work in thread executor"""
        try:
            logger.info(f"🎯 Executing {signal} for {symbol} on account {account_id}...")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self._execute_trade_sync(symbol, signal, account_id, config)
            )

            if result:
                # Async logging after sync MT5 work completes
                await self.log_trade(symbol, signal, result['entry_price'], result['lot_size'], account_id)

        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")

    def _execute_trade_sync(self, symbol: str, signal: str, account_id: int, config: dict) -> Optional[dict]:
        """Synchronous MT5 trade execution - runs in thread pool."""
        session = mt5_manager.get_session(account_id)
        if not session:
            logger.error(f"❌ Account {account_id} not found in manager")
            return None
        try:
            session.switch_to()  # Cached: fast if already on this account
        except Exception as e:
            logger.error(f"❌ Failed to switch to account {account_id}: {e}")
            return None

        account_info = mt5.account_info()
        if account_info is None:
            logger.error("❌ Failed to get account info")
            return None

        balance = account_info.balance
        free_margin = account_info.margin_free
        manual_lot_size = config.get('lot_size')
        lot_size = manual_lot_size if (manual_lot_size and manual_lot_size > 0) else self.calculate_lot_size(balance)

        # Guard: check margin required for the requested lot size.
        # order_send returns None (not an error object) when margin is insufficient,
        # so we validate upfront and fall back to auto-calculated size if needed.
        margin_check = mt5.order_calc_margin(
            mt5.ORDER_TYPE_BUY if signal == 'BUY' else mt5.ORDER_TYPE_SELL,
            symbol, lot_size, 0  # price 0 = use current market price
        )
        if margin_check is not None and margin_check > free_margin * 0.9:
            safe_lot = self.calculate_lot_size(balance)
            logger.warning(
                f"⚠️ Lot size {lot_size} requires ~${margin_check:.0f} margin but only "
                f"${free_margin:.0f} free. Falling back to {safe_lot} lots."
            )
            lot_size = safe_lot

        logger.info(f"💰 Account {account_id} balance: ${balance:.2f}, free margin: ${free_margin:.2f}, Lot size: {lot_size}")

        # Close opposite position synchronously (pass account_id to use correct position key)
        self._close_opposite_position_sync(symbol, account_id)

        sym_info = mt5.symbol_info(symbol)
        if sym_info is None:
            logger.error(f"❌ Symbol info not available for {symbol}")
            return None
        entry_price = float(sym_info.ask if signal == 'BUY' else sym_info.bid)
        order_type = mt5.ORDER_TYPE_BUY if signal == 'BUY' else mt5.ORDER_TYPE_SELL

        ticket = mt5.order_send({
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': lot_size,
            'type': order_type,
            'price': entry_price,
            'type_filling': mt5.ORDER_FILLING_IOC,
            'comment': f'Auto-Trade {signal} - Renko {config.get("brick_size", 1.0)}'
        })

        if ticket is None or ticket.retcode != mt5.TRADE_RETCODE_DONE:
            last_err = mt5.last_error()
            logger.error(
                f"❌ Trade failed for {symbol} on account {account_id}: "
                f"{ticket.comment if ticket else 'order_send returned None'} | "
                f"MT5 last error: {last_err}"
            )
            return None

        logger.info(f"✅ TRADE PLACED! Ticket: {ticket.order}, {signal} {lot_size} {symbol} @ {entry_price} (account {account_id})")
        pos_key = f"{account_id}_{symbol}"  # per-account key prevents cross-account overwrite
        self.open_positions[pos_key] = {
            'ticket': ticket.order, 'direction': signal, 'entry_price': entry_price,
            'lot_size': lot_size, 'opened_at': datetime.now().isoformat(), 'account_id': account_id,
        }
        return {'entry_price': entry_price, 'lot_size': lot_size}

    def _place_limit_order_sync(self, symbol: str, direction: str, limit_price: float,
                                account_id: int, config: dict) -> Optional[dict]:
        """Place a BUY_LIMIT or SELL_LIMIT pending order at the Renko brick close price."""
        session = mt5_manager.get_session(account_id)
        if not session:
            logger.error(f"❌ Account {account_id} not found")
            return None
        try:
            session.switch_to()
        except Exception as e:
            logger.error(f"❌ Failed to switch to account {account_id}: {e}")
            return None

        account_info = mt5.account_info()
        if account_info is None:
            logger.error("❌ Failed to get account info")
            return None

        balance = account_info.balance
        free_margin = account_info.margin_free
        manual_lot = config.get('lot_size')
        lot_size = manual_lot if (manual_lot and manual_lot > 0) else self.calculate_lot_size(balance)

        sym_info = mt5.symbol_info(symbol)
        if sym_info is None:
            logger.error(f"❌ Symbol info not available for {symbol}")
            return None

        limit_price = round(limit_price, sym_info.digits)
        order_type = mt5.ORDER_TYPE_BUY_LIMIT if direction == 'BUY' else mt5.ORDER_TYPE_SELL_LIMIT

        request = {
            'action': mt5.TRADE_ACTION_PENDING,
            'symbol': symbol,
            'volume': lot_size,
            'type': order_type,
            'price': limit_price,
            'type_time': mt5.ORDER_TIME_GTC,
            'comment': f'Renko {direction} LIMIT {config.get("brick_size", 1.0)}',
        }

        # Add SL/TP if configured (in pips)
        pip_size = sym_info.point * (10 if sym_info.digits % 2 == 1 else 1)
        sl_pips = config.get('stop_loss_pips', 0)
        tp_pips = config.get('take_profit_pips', 0)
        if sl_pips and sl_pips > 0:
            if direction == 'BUY':
                request['sl'] = round(limit_price - sl_pips * pip_size, sym_info.digits)
            else:
                request['sl'] = round(limit_price + sl_pips * pip_size, sym_info.digits)
        if tp_pips and tp_pips > 0:
            if direction == 'BUY':
                request['tp'] = round(limit_price + tp_pips * pip_size, sym_info.digits)
            else:
                request['tp'] = round(limit_price - tp_pips * pip_size, sym_info.digits)

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            last_err = mt5.last_error()
            logger.error(
                f"❌ Limit order failed for {symbol}: "
                f"{result.comment if result else 'order_send returned None'} | MT5: {last_err}"
            )
            return None

        logger.info(
            f"✅ LIMIT ORDER PLACED! Ticket: {result.order}, "
            f"{direction} LIMIT {lot_size} {symbol} @ {limit_price} (account {account_id})"
        )
        pos_key = f"{account_id}_{symbol}"
        self.open_positions[pos_key] = {
            'ticket': result.order, 'direction': direction, 'entry_price': limit_price,
            'lot_size': lot_size, 'opened_at': datetime.now().isoformat(),
            'account_id': account_id, 'order_type': 'LIMIT',
        }
        return {'ticket': result.order, 'lot_size': lot_size}

    def _cancel_pending_order_sync(self, symbol: str, account_id: int, ticket: int):
        """Cancel a specific pending limit order by ticket number."""
        try:
            result = mt5.order_send({'action': mt5.TRADE_ACTION_REMOVE, 'order': ticket})
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.warning(
                    f"⚠️ Could not cancel order {ticket} for {symbol}: "
                    f"{result.comment if result else 'None'} (may already be filled/expired)"
                )
            else:
                logger.info(f"🚫 Cancelled pending limit order {ticket} for {symbol}")
            self.open_positions.pop(f"{account_id}_{symbol}", None)
        except Exception as e:
            logger.error(f"❌ Error cancelling order {ticket}: {e}")

    def _close_opposite_position_sync(self, symbol: str, account_id: int = None):
        """Close any open MT5 position for the symbol synchronously. MT5 must already be switched."""
        try:
            pos_key = f"{account_id}_{symbol}" if account_id else symbol
            positions = mt5.positions_get(symbol=symbol)
            if positions is None or len(positions) == 0:
                self.open_positions.pop(pos_key, None)
                return

            for pos_info in positions:
                ticket = pos_info.ticket
                logger.info(f"📖 Closing position (Ticket: {ticket}, {pos_info.volume} lots)...")

                close_type = mt5.ORDER_TYPE_SELL if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
                close_price = mt5.symbol_info(symbol).bid if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info(symbol).ask

                close_order = mt5.order_send({
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol': symbol,
                    'volume': pos_info.volume,
                    'type': close_type,
                    'position': ticket,
                    'price': close_price,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                    'comment': 'Auto-Trade CLOSE'
                })

                if close_order is None or close_order.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.error(f"❌ Failed to close position {ticket}: {close_order.comment if close_order else 'None'}")
                else:
                    logger.info(f"✅ Position closed! Ticket: {close_order.order}")

            self.open_positions.pop(pos_key, None)

        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")
    
    async def log_trade(self, symbol: str, direction: str, entry_price: float, lot_size: float, account_id: int):
        """Log trade to Supabase"""
        try:
            if not self.supabase_client:
                return
            
            self.supabase_client.table('auto_trading_history').insert({
                'account_id': account_id,
                'symbol': symbol,
                'direction': direction,
                'entry_price': entry_price,
                'entry_time': datetime.now().isoformat(),
                'lot_size': lot_size,
                'reason': f'Renko brick color changed to {direction}',
            }).execute()
        except Exception as e:
            logger.error(f"❌ Failed to log trade: {e}")
    
    async def add_symbol(self, symbol: str, account_id: int, brick_size: float = 0.005):
        """Add symbol to auto-trading watchlist"""
        try:
            self.enabled_symbols[symbol] = {
                'account_id': account_id,
                'enabled': True,
                'brick_size': brick_size,
                'lot_size_rules': {
                    'balance_less_100': 0.001,
                    'balance_101_500': 0.01,
                    'balance_501_plus': 0.1
                },
                'created_at': datetime.now().isoformat(),
            }
            
            # Store in database
            if self.supabase_client:
                self.supabase_client.table('auto_trading_watchlist').insert({
                    'account_id': account_id,
                    'symbol': symbol,
                    'enabled': True,
                    'brick_size': brick_size,
                }).execute()
            
            logger.info(f"✅ Symbol {symbol} added to auto-trading")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add symbol: {e}")
            return False
    
    async def remove_symbol(self, symbol: str):
        """Remove symbol from auto-trading watchlist"""
        try:
            self.enabled_symbols.pop(symbol, None)
            self.last_brick_state.pop(symbol, None)
            
            # Close any open position
            pos = self.open_positions.pop(symbol, None)
            if pos and self.supabase_client:
                # Close in MT5
                ticket = pos['ticket']
                position = mt5.positions_get(ticket=ticket)
                if position:
                    pos_info = position[0]
                    mt5.order_send({
                        'action': mt5.TRADE_ACTION_DEAL,
                        'symbol': symbol,
                        'volume': pos_info.volume,
                        'type': mt5.ORDER_TYPE_SELL if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        'position': ticket,
                        'price': mt5.symbol_info(symbol).bid if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info(symbol).ask,
                    })
            
            # Update database
            if self.supabase_client:
                self.supabase_client.table('auto_trading_watchlist').update({
                    'enabled': False
                }).eq('symbol', symbol).execute()
            
            logger.info(f"✅ Symbol {symbol} removed from auto-trading")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to remove symbol: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get auto-trader service status"""
        # Infer running from last_evaluation being recent (within 60s)
        # is_running can be stale if the loop is running as a background task
        from datetime import datetime
        is_active = self.is_running or (
            hasattr(self, '_last_evaluation_time') and
            (datetime.now() - self._last_evaluation_time).total_seconds() < 60
        )
        return {
            'running': is_active,
            'enabled_symbols': list(self.enabled_symbols.keys()),
            'open_positions': self.open_positions,
            'last_evaluation': self._last_evaluation_time.isoformat() if hasattr(self, '_last_evaluation_time') else datetime.now().isoformat(),
        }


# Global instance — created once by start_auto_trading() at startup
auto_trader: Optional[AutoTrader] = None

async def get_auto_trader() -> AutoTrader:
    """Get or create global auto-trader instance"""
    global auto_trader
    if auto_trader is None:
        auto_trader = AutoTrader()
        await auto_trader.initialize()
    return auto_trader


async def start_auto_trading():
    """Start the auto-trading service (call from FastAPI startup)"""
    global auto_trader
    auto_trader = await get_auto_trader()
    asyncio.create_task(auto_trader.start())
    logger.info("🤖 Auto-Trading service started in background")




def get_auto_trader_instance() -> Optional['AutoTrader']:
    """Synchronous getter for the global auto-trader instance."""
    return auto_trader
async def stop_auto_trading():
    """Stop the auto-trading service (call from FastAPI shutdown)"""
    global auto_trader
    if auto_trader:
        await auto_trader.stop()
        logger.info("🤖 Auto-Trading service stopped")
