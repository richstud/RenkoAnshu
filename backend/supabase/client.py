from supabase import create_client
from backend.config import settings

# Use service role key if available — bypasses Row Level Security (RLS).
# Falls back to anon key for read-only public data.
_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
supabase_client = create_client(settings.SUPABASE_URL, _key)


def setup_schema() -> None:
    # Assumes table creation is handled outside with migrations.
    pass
