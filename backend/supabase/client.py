from supabase import create_client
from backend.config import settings

# Use service role key for backend (bypasses RLS securely)
# Falls back to anon key if service key not set
_backend_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
supabase_client = create_client(settings.SUPABASE_URL, _backend_key)


def setup_schema() -> None:
    # Assumes table creation is handled outside with migrations.
    pass
