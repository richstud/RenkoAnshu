"""
API endpoints for MT5 account management (link/unlink accounts)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["accounts"])

# Import MT5 manager and Supabase
from backend.mt5.connection import mt5_manager
from backend.supabase.client import supabase_client


class ConnectAccountRequest(BaseModel):
    login: int
    password: str
    server: str


class DisconnectAccountRequest(BaseModel):
    login: int


@router.post("/connect-account")
async def connect_account(request: ConnectAccountRequest):
    """Connect/Link a new MT5 account"""
    try:
        logger.info(f"🔐 Attempting to connect account {request.login} on {request.server}...")

        # Add account to MT5 manager
        mt5_manager.add_account(request.login, request.password, request.server)

        # Try to connect with a hard timeout so the HTTP request doesn't hang
        try:
            connected = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: mt5_manager.connect_account(request.login, max_retries=2)
                ),
                timeout=20.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="MT5 connection timed out. Ensure MT5 terminal is running and credentials are correct.")

        if not connected:
            raise HTTPException(status_code=400, detail="Failed to connect to MT5. Check login, password and server name.")

        # Get account info
        account_info = mt5_manager.get_account_info(request.login)
        if account_info is None:
            raise HTTPException(status_code=400, detail="Connected but could not retrieve account info")

        balance = float(account_info.balance)

        # Save to Supabase
        try:
            existing = supabase_client.table('accounts').select('*').eq('login', request.login).execute()
            if existing.data and len(existing.data) > 0:
                supabase_client.table('accounts').update({
                    'password': request.password,
                    'server': request.server,
                    'status': 'active',
                    'balance': balance
                }).eq('login', request.login).execute()
                logger.info(f"✅ Account {request.login} updated in database")
            else:
                supabase_client.table('accounts').insert({
                    'login': request.login,
                    'password': request.password,
                    'server': request.server,
                    'status': 'active',
                    'balance': balance
                }).execute()
                logger.info(f"✅ Account {request.login} added to database")
        except Exception as db_err:
            logger.warning(f"Could not save to database: {db_err}")

        # Notify auto-trader to reload watchlist so new account starts trading
        try:
            from backend.services.auto_trader import get_auto_trader_instance
            instance = get_auto_trader_instance()
            if instance and instance.is_running:
                asyncio.create_task(instance.load_watchlist())
                logger.info(f"Auto-trader notified to reload watchlist for new account {request.login}")
        except Exception as e:
            logger.warning(f"Could not notify auto-trader: {e}")

        return {
            "status": "success",
            "message": f"Account {request.login} connected successfully",
            "login": request.login,
            "server": request.server,
            "balance": balance
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to connect account {request.login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect-account")
async def disconnect_account(request: DisconnectAccountRequest):
    """Disconnect/Unlink an MT5 account"""
    try:
        login = request.login
        logger.info(f"🔓 Disconnecting account {login}...")

        # Remove from MT5 manager
        mt5_manager.remove_account(login)

        # Update Supabase
        try:
            supabase_client.table('accounts').update({
                'status': 'inactive'
            }).eq('login', login).execute()
            logger.info(f"✅ Account {login} marked as inactive")
        except Exception as db_err:
            logger.warning(f"Could not update database: {db_err}")

        # Notify auto-trader to stop monitoring this account
        try:
            from backend.services.auto_trader import get_auto_trader_instance
            instance = get_auto_trader_instance()
            if instance and instance.is_running:
                # Remove all symbol_keys for this account
                keys_to_remove = [k for k in instance.enabled_symbols if k.startswith(f"{login}_")]
                for k in keys_to_remove:
                    instance.enabled_symbols.pop(k, None)
                logger.info(f"Removed {len(keys_to_remove)} symbols from auto-trader for account {login}")
        except Exception as e:
            logger.warning(f"Could not notify auto-trader: {e}")

        return {
            "status": "success",
            "message": f"Account {login} disconnected",
            "login": login
        }

    except Exception as e:
        logger.error(f"❌ Failed to disconnect account {request.login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def get_accounts():
    """Get all connected MT5 accounts with live balance"""
    try:
        response = supabase_client.table('accounts').select('*').execute()

        accounts = []
        for account in response.data:
            login = account.get('login')
            # Check if currently connected in MT5 manager
            session = mt5_manager.get_session(login)
            is_live = session is not None and session.connected

            # Try to get live balance if connected
            balance = account.get('balance', 0)
            if is_live:
                try:
                    live_balance = session.get_balance()
                    if live_balance > 0:
                        balance = live_balance
                except Exception:
                    pass

            accounts.append({
                "id": account.get('id'),
                "login": login,
                "server": account.get('server'),
                "status": 'active' if is_live else account.get('status', 'inactive'),
                "balance": balance
            })

        logger.info(f"📋 Retrieved {len(accounts)} accounts")
        return accounts

    except Exception as e:
        logger.error(f"❌ Failed to get accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account/{login}")
async def get_account(login: int):
    """Get specific account info"""
    try:
        response = supabase_client.table('accounts').select('*').eq('login', login).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Account {login} not found")
        account = response.data[0]
        return {
            "id": account.get('id'),
            "login": account.get('login'),
            "server": account.get('server'),
            "status": account.get('status'),
            "balance": account.get('balance')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get account {login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    """
    Connect/Link a new MT5 account
    
    Args:
        login: MT5 account login number
        password: MT5 account password
        server: MT5 server name (e.g., 'ICMarkets')
    
    Returns:
        Success status and account info
    """
    try:
        logger.info(f"🔐 Attempting to connect account {request.login} on {request.server}...")
        
        # Add account to MT5 manager
        mt5_manager.add_account(request.login, request.password, request.server)
        
        # Try to connect
        if not mt5_manager.connect_account(request.login):
            raise HTTPException(status_code=400, detail="Failed to connect to MT5 account")
        
        # Get account info
        account_info = mt5_manager.get_account_info(request.login)
        if account_info is None:
            raise HTTPException(status_code=400, detail="Could not retrieve account info")
        
        # Save to Supabase (including password for auto-reconnect on startup)
        try:
            # Check if already exists
            existing = supabase_client.table('accounts').select('*').eq('login', request.login).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update
                supabase_client.table('accounts').update({
                    'password': request.password,
                    'server': request.server,
                    'status': 'active',
                    'balance': float(account_info.balance)
                }).eq('login', request.login).execute()
                
                logger.info(f"✅ Account {request.login} updated in database")
            else:
                # Insert new (WITH PASSWORD for auto-reconnect)
                supabase_client.table('accounts').insert({
                    'login': request.login,
                    'password': request.password,
                    'server': request.server,
                    'status': 'active',
                    'balance': float(account_info.balance)
                }).execute()
                
                logger.info(f"✅ Account {request.login} added to database with password")
        
        except Exception as db_err:
            logger.warning(f"Could not save to database: {db_err}")
        
        return {
            "status": "success",
            "message": f"Account {request.login} connected successfully",
            "login": request.login,
            "server": request.server,
            "balance": float(account_info.balance)
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to connect account {request.login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect-account")
async def disconnect_account(login: int = Query(...)):
    """
    Disconnect/Unlink an MT5 account
    
    Args:
        login: MT5 account login number
    
    Returns:
        Success status
    """
    try:
        logger.info(f"🔓 Disconnecting account {login}...")
        
        # Remove from MT5 manager
        mt5_manager.remove_account(login)
        
        # Update Supabase
        try:
            supabase_client.table('accounts').update({
                'status': 'inactive'
            }).eq('login', login).execute()
            
            logger.info(f"✅ Account {login} marked as inactive")
        except Exception as db_err:
            logger.warning(f"Could not update database: {db_err}")
        
        return {
            "status": "success",
            "message": f"Account {login} disconnected",
            "login": login
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to disconnect account {login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def get_accounts():
    """
    Get all connected MT5 accounts
    
    Returns:
        List of account info
    """
    try:
        response = supabase_client.table('accounts').select('*').execute()
        
        accounts = []
        for account in response.data:
            accounts.append({
                "id": account.get('id'),
                "login": account.get('login'),
                "server": account.get('server'),
                "status": account.get('status', 'unknown'),
                "balance": account.get('balance', 0)
            })
        
        logger.info(f"📋 Retrieved {len(accounts)} accounts")
        return accounts
    
    except Exception as e:
        logger.error(f"❌ Failed to get accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account/{login}")
async def get_account(login: int):
    """
    Get specific account info
    
    Args:
        login: MT5 account login number
    
    Returns:
        Account details
    """
    try:
        response = supabase_client.table('accounts').select('*').eq('login', login).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Account {login} not found")
        
        account = response.data[0]
        return {
            "id": account.get('id'),
            "login": account.get('login'),
            "server": account.get('server'),
            "status": account.get('status'),
            "balance": account.get('balance')
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get account {login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
