from supabase import create_client
from backend.config import settings

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def setup_schema() -> None:
    # Assumes table creation is handled outside with migrations.
    pass
