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

    def connect(self):
        if not mt5.initialize(path=settings.MT5_PATH):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

        if not mt5.login(self.login, password=self.password, server=self.server):
            raise RuntimeError(f"MT5 login failed {self.login}@{self.server}: {mt5.last_error()}")

        self.connected = True
        self.account_info = mt5.account_info()  # type: ignore
        logger.info(f"Connected account {self.login}")

    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info(f"Disconnected account {self.login}")

    def get_balance(self) -> float:
        if not self.connected:
            self.connect()
        ai = mt5.account_info()  # type: ignore
        return float(ai.balance) if ai else 0.0

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

    def connect_all(self):
        for session in self.sessions.values():
            retry = 3
            while retry > 0:
                try:
                    session.connect()
                    break
                except Exception as exc:
                    logger.error(f"Failed connecting {session.login}: {exc}")
                    retry -= 1
                    time.sleep(2)

    def disconnect_all(self):
        for session in self.sessions.values():
            session.disconnect()

    def get_session(self, login: int) -> Optional[AccountSession]:
        return self.sessions.get(login)

mt5_manager = MT5Manager()
