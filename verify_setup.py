#!/usr/bin/env python3
"""
Quick setup verification script for Renko Trading Bot
Run this to verify all components are correctly configured
"""

import sys
import os
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print_section("🐍 Python Version Check")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 11:
        print("✅ Python version is suitable (3.11+)")
        return True
    else:
        print("❌ Python 3.11 or higher required")
        print(f"   Current: {version.major}.{version.minor}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    print_section("🔑 Environment Configuration Check")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print(f"   Expected at: {env_path.resolve()}")
        return False
    
    print(f"✅ .env file found: {env_path.resolve()}")
    
    # Read and check required keys
    required_keys = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "MT5_PATH",
        "MT5_LOGIN",
        "MT5_PASSWORD",
        "MT5_SERVER",
    ]
    
    with open(env_path) as f:
        env_content = f.read()
    
    missing_keys = []
    for key in required_keys:
        if key not in env_content:
            missing_keys.append(key)
        else:
            print(f"  ✅ {key} configured")
    
    if missing_keys:
        print(f"\n⚠️  Missing configuration keys: {', '.join(missing_keys)}")
        return False
    
    print("\n✅ All required environment variables configured")
    return True

def check_dependencies():
    """Check if Python dependencies are installed"""
    print_section("📦 Python Dependency Check")
    
    required_packages = {
        "fastapi": "FastAPI Framework",
        "uvicorn": "ASGI Server",
        "pydantic": "Data Validation",
        "pydantic_settings": "Configuration Management",
        "supabase": "Supabase Client",
        "MetaTrader5": "MT5 Connection",
        "dotenv": "Environment Variables",
    }
    
    installed = []
    missing = []
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace("-", "_"))
            installed.append(f"  ✅ {package:20} ({description})")
        except ImportError:
            missing.append(f"  ❌ {package:20} ({description})")
    
    for item in installed:
        print(item)
    
    for item in missing:
        print(item)
    
    if missing:
        print(f"\n⚠️  {len(missing)} packages missing. Install with:")
        print("   pip install -r requirements.txt")
        return False
    
    print(f"\n✅ All {len(installed)} required packages installed")
    return True

def check_supabase_connection():
    """Test Supabase connectivity"""
    print_section("🔗 Supabase Connection Check")
    
    try:
        from backend.supabase.client import supabase_client
        
        # Try a simple query
        result = supabase_client.table("accounts").select("*").limit(1).execute()
        print("✅ Successfully connected to Supabase")
        
        # Check if tables exist
        tables_to_check = [
            "accounts",
            "watchlist",
            "trades",
            "logs",
            "settings",
            "bot_control",
            "available_symbols",
        ]
        
        existing_tables = []
        for table in tables_to_check:
            try:
                supabase_client.table(table).select("*").limit(1).execute()
                existing_tables.append(table)
                print(f"  ✅ Table '{table}' exists")
            except Exception as e:
                print(f"  ⚠️  Table '{table}' might not exist: {str(e)[:50]}")
        
        if len(existing_tables) < len(tables_to_check):
            print(f"\n⚠️  {len(tables_to_check) - len(existing_tables)} tables missing")
            print("   Run SQL schema initialization:")
            print("   1. Supabase Dashboard > SQL Editor")
            print("   2. Copy-paste: backend/supabase/schema.sql")
            print("   3. Click 'Run'")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("\nCheck your .env file:")
        print("  - SUPABASE_URL correct?")
        print("  - SUPABASE_KEY correct?")
        print("  - Internet connection stable?")
        return False

def check_frontend_config():
    """Check frontend configuration"""
    print_section("⚛️  Frontend Configuration Check")
    
    # Check if frontend folder exists
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ frontend/ directory not found")
        return False
    
    print(f"✅ frontend/ directory found: {frontend_path.resolve()}")
    
    # Check package.json
    package_json = frontend_path / "package.json"
    if package_json.exists():
        print("✅ package.json found")
    else:
        print("❌ package.json not found")
        return False
    
    # Check .env
    frontend_env = frontend_path / ".env"
    if frontend_env.exists():
        with open(frontend_env) as f:
            content = f.read()
            if "VITE_API_URL" in content:
                print("✅ frontend/.env configured with VITE_API_URL")
            else:
                print("⚠️  VITE_API_URL not found in frontend/.env")
    else:
        print("⚠️  frontend/.env not found (will use default)")
    
    print("\nNext step: npm install && npm run dev")
    return True

def check_structure():
    """Check project structure"""
    print_section("📁 Project Structure Check")
    
    required_dirs = {
        "backend": "Backend Python code",
        "frontend": "Frontend React code",
        "backend/api": "API endpoints",
        "backend/supabase": "Supabase configuration",
        "backend/mt5": "MT5 connection module",
        "backend/execution": "Trade execution module",
    }
    
    all_exist = True
    for dir_path, description in required_dirs.items():
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path:30} ({description})")
        else:
            print(f"❌ {dir_path:30} ({description})")
            all_exist = False
    
    return all_exist

def print_summary(checks):
    """Print final summary"""
    print_section("📊 Verification Summary")
    
    passed = sum(1 for check in checks if check)
    total = len(checks)
    
    print(f"Passed: {passed}/{total} checks\n")
    
    if passed == total:
        print("✅ All checks passed! You're ready to test:")
        print("\n1. Start Backend:")
        print("   .venv\\Scripts\\activate")
        print("   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\n2. Start Frontend (in another terminal):")
        print("   cd frontend")
        print("   npm run dev")
        print("\n3. Open: http://localhost:5173")
        print("\n" + "="*60)
        return True
    else:
        print(f"⚠️  {total - passed} check(s) failed. Fix issues above and re-run.\n")
        print("Need help? See TESTING_SETUP.md in project root")
        print("="*60)
        return False

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  🚀 Renko Trading Bot - Setup Verification")
    print("="*60)
    
    checks = [
        check_python_version(),
        check_env_file(),
        check_dependencies(),
        check_structure(),
        check_frontend_config(),
    ]
    
    # Only check Supabase if dependencies are OK
    if checks[2]:  # dependencies check
        checks.append(check_supabase_connection())
    else:
        print_section("🔗 Supabase Connection Check")
        print("⏭️  Skipped (dependencies not installed)")
        checks.append(False)
    
    success = print_summary(checks)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
