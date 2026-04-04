from pydantic import BaseSettings

class Settings(BaseSettings):
    MT5_PATH: str = ""
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_SCHEMA: str = "public"
    RENKO_BRICK_SIZE: float = 1.0
    SYMBOL: str = "XAUUSD"
    POLL_INTERVAL: float = 0.5
    MAX_TRADE_SIDE: int = 1
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
