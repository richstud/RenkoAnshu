from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str = ""  # Service role key — bypasses RLS
    SUPABASE_DB_SCHEMA: str = "public"
    
    # MT5
    MT5_PATH: str = ""
    MT5_LOGIN: str = ""
    MT5_PASSWORD: str = ""
    MT5_SERVER: str = ""
    
    # Renko Strategy
    RENKO_BRICK_SIZE: float = 1.0
    SYMBOL: str = "XAUUSD"
    POLL_INTERVAL: float = 0.5
    
    # Bot Config
    MAX_TRADE_SIDE: int = 1
    environment: str = "development"
    
    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
