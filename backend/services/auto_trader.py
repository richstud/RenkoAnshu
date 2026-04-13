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
        self.open_positions: Dict[str, dict] = {}  # {symbol: {ticket, direction, entry_price, ...}}
        self.is_running = False
        self.supabase_client = None
        
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
        """Load auto-trading watchlist from Supabase for ALL accounts with enabled symbols"""
        try:
            if not self.supabase_client:
                logger.warning("Supabase client not initialized")
                return
            
            # Fetch all enabled symbols across all accounts
            response = self.supabase_client.table('watchlist').select('*').eq('algo_enabled', True).execute()
            
            # Group by account_id to track accounts and their enabled symbols
            accounts_symbols = {}
            
            for item in response.data:
                symbol = item['symbol']
                account_id = item['account_id']
                
                # Create key combining account and symbol for unique tracking
                symbol_key = f"{account_id}_{symbol}"
                
                self.enabled_symbols[symbol_key] = {
                    'symbol': symbol,
                    'account_id': account_id,
                    'algo_enabled': True,
                    'lot_size': item.get('lot_size', 0.01),
                    'brick_size': item.get('brick_size', 1.0),
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
        """Evaluate strategy for all enabled symbols on all accounts and execute trades"""
        try:
            for symbol_key in list(self.enabled_symbols.keys()):
                await self.evaluate_symbol(symbol_key)
        except Exception as e:
            logger.error(f"❌ Strategy evaluation error: {e}")
    
    async def evaluate_symbol(self, symbol_key: str):
        """Evaluate strategy for a specific account+symbol pair"""
        try:
            config = self.enabled_symbols.get(symbol_key)
            if not config or not config.get('algo_enabled', False):
                return
            
            account_id = config['account_id']
            symbol = config['symbol']  # Extract the actual symbol (e.g., 'BTCUSD')
            brick_size = config.get('brick_size', 1.0)
            
            # Ensure account is connected
            session = mt5_manager.get_session(account_id)
            if not session:
                logger.warning(f"⚠️ Account {account_id} not found in manager")
                return
            
            try:
                session.ensure_connected()
            except Exception as e:
                logger.warning(f"⚠️ Account {account_id} connection issue: {e}. Will retry on next cycle.")
                return
            
            # Check if account is actually connected
            if not session.connected:
                logger.debug(f"⏳ Account {account_id} not yet connected, skipping evaluation")
                return
            
            # Fetch latest 1-min candles using ACTUAL SYMBOL, not the key
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
            if rates is None or len(rates) == 0:
                logger.debug(f"⏳ No rate data yet for {symbol}")
                return
            
            logger.debug(f"📈 Got {len(rates)} rates for {symbol}")
            
            # Get or create Renko engine
            engine_key = f"{symbol}_{brick_size}"
            if engine_key not in self.renko_engines:
                logger.info(f"🏗️ Creating Renko engine for {symbol} with brick_size={brick_size}")
                self.renko_engines[engine_key] = RenkoEngine(brick_size)
                self.strategy_engines[engine_key] = StrategyEngine(self.renko_engines[engine_key])
            
            renko = self.renko_engines[engine_key]
            
            # ─── CRITICAL FIX: only feed candles we haven't seen yet ───────────
            last_fed_time = self.last_candle_times.get(engine_key, 0)
            if last_fed_time == 0:
                # First run: initialize engine with full history
                new_rates = list(rates)
                logger.info(f"📊 Initializing Renko engine for {symbol} with {len(new_rates)} historical candles")
            else:
                # Subsequent runs: only NEW candles (time > last fed)
                new_rates = [r for r in rates if int(r['time']) > last_fed_time]
            
            if new_rates:
                for rate in new_rates:
                    renko.feed_tick(rate['close'])
                self.last_candle_times[engine_key] = int(new_rates[-1]['time'])
                logger.debug(f"Fed {len(new_rates)} new candle(s) to {symbol} Renko engine")
            # ──────────────────────────────────────────────────────────────────
            
            # Get current brick color
            all_bricks = renko.history(10)
            if len(all_bricks) == 0:
                logger.info(f"⏳ [{symbol}] No bricks generated yet (need more price movement with brick_size={brick_size})")
                return
            
            current_brick = all_bricks[-1]
            current_color = current_brick.color  # 'green' or 'red'
            last_color = self.last_brick_state.get(symbol_key)
            
            # Log Renko state (debug)
            if last_color is None:
                logger.info(f"📊 [{symbol}] Renko initialized with {len(all_bricks)} bricks, current color: {current_color}")
            
            # Store current color using the symbol_key to track per account
            self.last_brick_state[symbol_key] = current_color
            
            # Check if color changed (new signal)
            if last_color is None or last_color == current_color:
                # No signal yet or color didn't change
                return
            
            # Signal detected!
            logger.info(f"📊 Signal detected for {symbol}: {last_color} → {current_color}, brick_size={brick_size}")
            
            # Determine signal
            if current_color == 'green':
                signal = 'BUY'
            else:
                signal = 'SELL'
            
            # Execute trade
            await self.execute_trade(symbol, signal, account_id, config)
        
        except Exception as e:
            logger.error(f"❌ Error evaluating {symbol}: {e}")
    
    async def execute_trade(self, symbol: str, signal: str, account_id: int, config: dict):
        """Execute a trade based on signal"""
        try:
            logger.info(f"🎯 Executing {signal} for {symbol} on account {account_id}...")
            
            # Ensure account is connected
            session = mt5_manager.get_session(account_id)
            if not session:
                logger.error(f"❌ Account {account_id} not found in manager")
                return
            
            # Check connection
            if not session.connected:
                logger.warning(f"⚠️ Account {account_id} not connected, attempting to connect...")
                try:
                    session.connect()
                except Exception as e:
                    logger.error(f"❌ Failed to connect account {account_id}: {e}")
                    return
            
            session.ensure_connected()
            
            # Get account balance for lot sizing
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("❌ Failed to get account info")
                return
            
            balance = account_info.balance
            # Check if manual lot size is set in watchlist config (priority over calculated)
            manual_lot_size = config.get('lot_size')
            if manual_lot_size and manual_lot_size > 0:
                lot_size = manual_lot_size
                logger.info(f"💰 Account {account_id} balance: ${balance:.2f}, Using manual lot size: {lot_size}")
            else:
                # Calculate lot size based on account balance (dynamic sizing) - fallback
                lot_size = self.calculate_lot_size(balance)
                logger.info(f"💰 Account {account_id} balance: ${balance:.2f}, Calculated lot size: {lot_size}")
            
            # Close opposite position if exists
            await self.close_opposite_position(symbol, account_id)
            
            # Place new trade
            entry_price = float(mt5.symbol_info(symbol).ask if signal == 'BUY' else mt5.symbol_info(symbol).bid)
            
            if signal == 'BUY':
                ticket = mt5.order_send({
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol': symbol,
                    'volume': lot_size,
                    'type': mt5.ORDER_TYPE_BUY,
                    'price': entry_price,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                    'comment': f'Auto-Trade BUY - Renko {config.get("brick_size", 0.005)}'
                })
            else:  # SELL
                ticket = mt5.order_send({
                    'action': mt5.TRADE_ACTION_DEAL,
                    'symbol': symbol,
                    'volume': lot_size,
                    'type': mt5.ORDER_TYPE_SELL,
                    'price': entry_price,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                    'comment': f'Auto-Trade SELL - Renko {config.get("brick_size", 0.005)}'
                })
            
            if ticket is None or ticket.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"❌ Trade failed for {symbol} on account {account_id}: {ticket.comment if ticket else 'Unknown error'}")
                return
            
            logger.info(f"✅ TRADE PLACED! Ticket: {ticket.order}, {signal} {lot_size} {symbol} @ {entry_price} on account {account_id}")
            
            # Store position
            self.open_positions[symbol] = {
                'ticket': ticket.order,
                'direction': signal,
                'entry_price': entry_price,
                'lot_size': lot_size,
                'opened_at': datetime.now().isoformat(),
                'account_id': account_id,
            }
            
            # Log to database
            await self.log_trade(symbol, signal, entry_price, lot_size, account_id)
        
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
    
    async def close_opposite_position(self, symbol: str, account_id: int):
        """Close any opposite open position for the symbol"""
        try:
            # Check if we have an open position
            pos = self.open_positions.get(symbol)
            if not pos:
                return
            
            ticket = pos['ticket']
            logger.info(f"📖 Closing opposite position (Ticket: {ticket})...")
            
            # Get position details
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                logger.warning(f"Position {ticket} not found")
                self.open_positions.pop(symbol, None)
                return
            
            pos_info = position[0]
            
            # Close position
            close_order = mt5.order_send({
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': pos_info.volume,
                'type': mt5.ORDER_TYPE_SELL if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                'position': ticket,
                'price': mt5.symbol_info(symbol).bid if pos_info.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info(symbol).ask,
                'type_filling': mt5.ORDER_FILLING_IOC,
                'comment': f'Auto-Trade CLOSE'
            })
            
            if close_order.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"❌ Failed to close position: {close_order.comment}")
                return
            
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
        return {
            'running': self.is_running,
            'enabled_symbols': list(self.enabled_symbols.keys()),
            'open_positions': self.open_positions,
            'last_evaluation': datetime.now().isoformat(),
        }


# Global instance
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


async def stop_auto_trading():
    """Stop the auto-trading service (call from FastAPI shutdown)"""
    global auto_trader
    if auto_trader:
        await auto_trader.stop()
        logger.info("🤖 Auto-Trading service stopped")
