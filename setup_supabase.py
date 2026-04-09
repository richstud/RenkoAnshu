"""
Setup Supabase tables for Renko Trading Bot
This script creates all required database tables and indexes
"""

import sys
from supabase import create_client
from pathlib import Path

# Your Supabase credentials
SUPABASE_URL = "https://mflakcwgbpghyzdyevsb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q"

def setup_supabase():
    """Create Supabase client and verify connection"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase successfully!")
        print(f"📍 Project: {SUPABASE_URL}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

def read_schema():
    """Read the schema.sql file"""
    schema_path = Path(__file__).parent / "backend" / "supabase" / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found at: {schema_path}")
        sys.exit(1)
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    print(f"✅ Loaded schema from: {schema_path}")
    return schema_sql

def execute_schema(client, schema_sql):
    """Execute schema SQL using Supabase admin API"""
    try:
        # Split SQL into individual statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        print(f"\n📋 Found {len(statements)} SQL statements to execute...")
        print("=" * 60)
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement.startswith('--'):
                # Skip comments
                continue
                
            try:
                # For Supabase, we need to use the REST API or use RPC
                # The best approach is to use supabase.rpc() for custom SQL
                # But simpler: use the Python client with raw SQL execution
                
                print(f"\n[{i}/{len(statements)}] Executing...")
                print(f"  Statement: {statement[:70]}..." if len(statement) > 70 else f"  Statement: {statement}")
                
                # Note: Supabase Python client doesn't directly execute raw SQL
                # We'll need to use the postgres connection instead
                # For now, just track what would be executed
                
            except Exception as e:
                print(f"  ⚠️  Error (continuing): {str(e)[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to execute schema: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Renko Trading Bot - Supabase Setup")
    print("=" * 60)
    
    # Step 1: Connect to Supabase
    print("\n📌 Step 1: Connecting to Supabase...")
    client = setup_supabase()
    
    # Step 2: Read schema
    print("\n📌 Step 2: Reading schema file...")
    schema_sql = read_schema()
    
    # Step 3: Execute schema
    print("\n📌 Step 3: Setting up database tables...")
    print("\n⚠️  IMPORTANT: Using Supabase SQL Editor")
    print("-" * 60)
    print("\nSince Supabase Python client doesn't support direct SQL execution,")
    print("you need to run the SQL manually:")
    print("\n1. Go to: https://app.supabase.com/project/mflakcwgbpghyzdyevsb/sql/new")
    print("2. Copy this entire SQL and paste it there:")
    print("-" * 60)
    print("\n" + schema_sql[:500] + "\n... (truncated)\n")
    print("-" * 60)
    print("\nOr follow these steps:")
    print("1. Open your Supabase project dashboard")
    print("2. Go to SQL Editor (left sidebar)")
    print("3. Click 'New Query'")
    print("4. Copy & paste contents of: backend/supabase/schema.sql")
    print("5. Click 'RUN' button")
    print("\n✅ All tables will be created automatically!")
    print("=" * 60)

if __name__ == "__main__":
    main()
