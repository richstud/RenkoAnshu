"""
Real-Time Automated Trading Service
Monitors enabled symbols and executes trades based on Renko brick color changes
"""
import asyncio
import logging
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
        self.is_running = False
        self.supabase_client = None
        # Minimum seconds between trades per symbol (prevents rapid re-entry on noisy bricks)
        # NOTE: removed - using always-in strategy with $50 brick as noise filter
        
    async def initialize(self):
        """Initialize auto-trader service"""
        try:
            logger.info("🤖 Initializing Auto-Trader Service...")
            
            # Initialize Supabase client
            from supabase import create_client
            self.supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            
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
            active_accounts_res = self.supabase_client.table('accounts').select('login').eq('status', 'active').execute()
            active_logins = {str(row['login']) for row in (active_accounts_res.data or [])}
            
            # Fetch all enabled symbols across all accounts
            response = self.supabase_client.table('watchlist').select('*').eq('algo_enabled', True).execute()
            
            # Group by account_id to track accounts and their enabled symbols
            accounts_symbols = {}
            
            for item in response.data:
                symbol = item['symbol']
                account_id = item['account_id']
                
                # Skip symbols belonging to inactive/disconnected accounts
                if str(account_id) not in active_logins:
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
        
        try:
            reload_counter = 0
            while self.is_running:
                # Reload watchlist every 30 seconds to pick up new symbols added from UI
                if reload_counter % 30 == 0:
                    await self.load_watchlist()
                
                await self.evaluate_strategy()
                # Evaluate every 1 second, but strategy only runs on 1-min candle close
                await asyncio.sleep(1)
                reload_counter += 1
        except Exception as e:
            logger.error(f"❌ Auto-Trader error: {e}")
            self.is_running = False
    
    async def stop(self):
        """Stop the auto-trading service"""
        logger.info("⏹️ Stopping Auto-Trader service...")
        self.is_running = False
    
    async def evaluate_strategy(self):
        """Evaluate strategy for all symbols - runs sync MT5 work in thread to avoid blocking event loop"""
        try:
            loop = asyncio.get_event_loop()
            signals = await loop.run_in_executor(None, self._collect_signals_sync)
            self._last_evaluation_time = datetime.now()  # Track last successful evaluation
            for sig in signals:
                await self.execute_trade(sig['symbol'], sig['signal'], sig['account_id'], sig['config'])
        except Exception as e:
            logger.error(f"❌ Strategy evaluation error: {e}")

    def _collect_signals_sync(self) -> list:
        """Synchronous signal collection - runs in thread pool.
        Groups symbols by account to minimize mt5.login() calls (one per account switch).
        Returns list of {symbol, signal, account_id, config} dicts.
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
                session.switch_to()  # ONE login call per account (cached if same)
            except Exception as e:
                logger.warning(f"⚠️ Account {account_id} switch failed: {e}")
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
        """Pure sync: check Renko signal for one symbol. MT5 must already be switched to account."""
        symbol = config['symbol']
        brick_size = config.get('brick_size', 1.0)

        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
        if rates is None or len(rates) == 0:
            logger.debug(f"⏳ No rate data yet for {symbol}")
            return None

        # Include account_id so each account has its own independent Renko engine.
        # Without this, accounts sharing the same symbol+brick_size share one engine,
        # so only the first account to process each candle fires a signal.
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
                renko.feed_tick(rate['close'])
            self.last_candle_times[engine_key] = max(int(r['time']) for r in new_rates)
            logger.debug(f"Fed {len(new_rates)} new candle(s) to {symbol}")

        all_bricks = renko.history(10)
        if len(all_bricks) == 0:
            logger.info(f"⏳ [{symbol}] No bricks generated yet (need more price movement with brick_size={brick_size})")
            return None

        current_color = all_bricks[-1].color
        last_color = self.last_brick_state.get(symbol_key)

        if last_color is None:
            if len(all_bricks) >= 2:
                last_color = all_bricks[-2].color
                logger.info(f"📊 [{symbol}] Initialized: prev={last_color}, current={current_color}")
            else:
                self.last_brick_state[symbol_key] = current_color
                return None

        self.last_brick_state[symbol_key] = current_color

        if last_color == current_color:
            return None

        signal = 'BUY' if current_color == 'green' else 'SELL'
        logger.info(f"📊 Signal: {symbol} on account {account_id}: {last_color} → {current_color} → {signal}")
        return {'symbol': symbol, 'signal': signal, 'account_id': account_id, 'config': config}

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
        sig = self._check_signal_sync(symbol_key, config, account_id)
        if sig:
            await self.execute_trade(sig['symbol'], sig['signal'], sig['account_id'], sig['config'])
    
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
        manual_lot_size = config.get('lot_size')
        lot_size = manual_lot_size if (manual_lot_size and manual_lot_size > 0) else self.calculate_lot_size(balance)
        logger.info(f"💰 Account {account_id} balance: ${balance:.2f}, Lot size: {lot_size}")

        # Close opposite position synchronously
        self._close_opposite_position_sync(symbol)

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
            logger.error(f"❌ Trade failed for {symbol} on account {account_id}: {ticket.comment if ticket else 'None'}")
            return None

        logger.info(f"✅ TRADE PLACED! Ticket: {ticket.order}, {signal} {lot_size} {symbol} @ {entry_price} (account {account_id})")
        pos_key = f"{account_id}_{symbol}"  # per-account key prevents cross-account overwrite
        self.open_positions[pos_key] = {
            'ticket': ticket.order, 'direction': signal, 'entry_price': entry_price,
            'lot_size': lot_size, 'opened_at': datetime.now().isoformat(), 'account_id': account_id,
        }
        return {'entry_price': entry_price, 'lot_size': lot_size}

    def _close_opposite_position_sync(self, symbol: str):
        """Close any open MT5 position for the symbol synchronously. MT5 must already be switched."""
        try:
            # MT5 must already be switched to account_id by the caller (execute_trade does this)
            # Check MT5 directly for open positions on this symbol
            positions = mt5.positions_get(symbol=symbol)
            if positions is None or len(positions) == 0:
                self.open_positions.pop(symbol, None)
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

            self.open_positions.pop(symbol, None)

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


# Global instance
auto_trader: Optional[AutoTrader] = None

def get_auto_trader_instance() -> Optional[AutoTrader]:
    """Return the running auto_trader instance (for use by other modules)"""
    return auto_trader

# Alias for convenience
auto_trader_instance = auto_trader  # updated by start_auto_trading

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


async def stop_auto_trading():
    """Stop the auto-trading service (call from FastAPI shutdown)"""
    global auto_trader
    if auto_trader:
        await auto_trader.stop()
        logger.info("🤖 Auto-Trading service stopped")
