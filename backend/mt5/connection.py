import logging
import time
from typing import Dict, Optional

import MetaTrader5 as mt5

from backend.config import settings

logger = logging.getLogger("mt5")

class AccountSession:
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.account_info = None
        self.last_connection_attempt = 0
        self.connection_attempt_count = 0

    def connect(self, max_retries: int = 5, initial_delay: float = 1.0):
        """Connect to MT5 with exponential backoff retry logic
        
        Args:
            max_retries: Maximum number of connection attempts
            initial_delay: Initial delay between retries (seconds)
        """
        for attempt in range(max_retries):
            try:
                # Check if MT5 terminal is responding before attempting connection
                if attempt > 0:
                    try:
                        platform_info = mt5.terminal_info()
                        if not platform_info:
                            logger.warning(f"MT5 terminal not responding, attempt {attempt + 1}/{max_retries}")
                            delay = initial_delay * (2 ** attempt)  # Exponential backoff
                            time.sleep(min(delay, 10))  # Cap delay at 10 seconds
                            continue
                    except Exception as term_check_error:
                        logger.warning(f"MT5 terminal check failed: {term_check_error}")
                
                logger.info(f"Attempting to initialize MT5 (attempt {attempt + 1}/{max_retries})...")
                if not mt5.initialize(path=settings.MT5_PATH, timeout=10000):
                    error_info = mt5.last_error()
                    logger.warning(f"MT5 initialize attempt {attempt + 1} failed: {error_info}")
                    
                    # IPC timeout typically means MT5 terminal is not running
                    if error_info and "IPC timeout" in str(error_info):
                        delay = initial_delay * (2 ** attempt)
                        delay = min(delay, 10)
                        logger.info(f"IPC timeout detected. Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                    raise RuntimeError(f"MT5 initialize failed: {error_info}")
                
                time.sleep(1)  # Give MT5 time to initialize
                
                logger.info(f"Attempting to login account {self.login}@{self.server} (attempt {attempt + 1}/{max_retries})...")
                if not mt5.login(int(self.login), password=self.password, server=self.server, timeout=10000):
                    error_info = mt5.last_error()
                    logger.warning(f"MT5 login attempt {attempt + 1} failed for {self.login}: {error_info}")
                    
                    if error_info and "IPC timeout" in str(error_info):
                        delay = initial_delay * (2 ** attempt)
                        delay = min(delay, 10)
                        logger.info(f"IPC timeout on login. Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                        continue
                    raise RuntimeError(f"MT5 login failed {self.login}@{self.server}: {error_info}")
                
                self.account_info = mt5.account_info()
                self.connected = True
                self.connection_attempt_count = 0
                logger.info(f"✅ Successfully connected account {self.login}")
                return
            
            except RuntimeError as e:
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    delay = min(delay, 10)
                    logger.info(f"Connection failed, retrying in {delay:.1f}s... ({attempt + 2}/{max_retries})")
                    time.sleep(delay)
                else:
                    self.connection_attempt_count += 1
                    raise
            
            except Exception as e:
                logger.error(f"Unexpected error during connection attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    delay = min(delay, 10)
                    time.sleep(delay)
                else:
                    self.connection_attempt_count += 1
                    raise

    def disconnect(self):
        if self.connected:
            try:
                mt5.logout()
            except Exception as e:
                logger.warning(f"Error during MT5 logout: {e}")
            self.connected = False
            logger.info(f"Disconnected account {self.login}")

    def get_balance(self) -> float:
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                logger.error(f"Failed to connect when getting balance: {e}")
                return 0.0
        try:
            ai = mt5.account_info()
            return float(ai.balance) if ai else 0.0
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            self.connected = False
            return 0.0

    def ensure_connected(self):
        if not self.connected:
            self.connect()


class MT5Manager:
    def __init__(self):
        self.sessions: Dict[int, AccountSession] = {}

    def add_account(self, login: int, password: str, server: str):
        self.sessions[login] = AccountSession(login, password, server)

    def remove_account(self, login: int):
        session = self.sessions.pop(login, None)
        if session:
            session.disconnect()

    def connect_all(self, max_retries: int = 5):
        """Connect all accounts with improved retry logic
        
        Args:
            max_retries: Maximum retry attempts per account
        """
        if not self.sessions:
            logger.warning("No accounts to connect")
            return
        
        logger.info(f"🔗 Connecting {len(self.sessions)} account(s)...")
        successful_connections = 0
        failed_connections = []
        
        for login, session in self.sessions.items():
            try:
                logger.info(f"📍 Processing account {login}...")
                session.connect(max_retries=max_retries)
                successful_connections += 1
                logger.info(f"✅ Account {login} connected successfully")
            except Exception as exc:
                logger.error(f"❌ Failed to connect account {login}: {exc}")
                failed_connections.append((login, str(exc)))
        
        logger.info(f"📊 Connection summary: {successful_connections} succeeded, {len(failed_connections)} failed")
        
        if failed_connections:
            logger.warning("Failed accounts:")
            for login, error in failed_connections:
                logger.warning(f"  - Account {login}: {error}")

    def disconnect_all(self):
        for session in self.sessions.values():
            session.disconnect()

    def get_session(self, login: int) -> Optional[AccountSession]:
        return self.sessions.get(login)

    def connect_account(self, login: int, max_retries: int = 5) -> bool:
        """Connect a specific account with retry logic
        
        Args:
            login: Account login
            max_retries: Maximum retry attempts
            
        Returns:
            True if connected successfully, False otherwise
        """
        session = self.sessions.get(login)
        if not session:
            logger.error(f"Account {login} not found in sessions")
            return False
        try:
            session.connect(max_retries=max_retries)
            return True
        except Exception as e:
            logger.error(f"Failed to connect account {login}: {e}")
            return False

    def get_account_info(self, login: int):
        """Get account info for a specific account"""
        session = self.sessions.get(login)
        if not session:
            return None
        try:
            session.ensure_connected()
            return session.account_info
        except Exception as e:
            logger.error(f"Failed to get account info for {login}: {e}")
            return None

mt5_manager = MT5Manager()
