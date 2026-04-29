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
    """Connect/Link a new MT5 account.
    
    Saves credentials to DB immediately so account is registered even if MT5 is busy.
    Then tries to verify via MT5 with a short timeout.
    """
    try:
        logger.info(f"🔐 Registering account {request.login} on {request.server}...")

        # Step 1: Save to Supabase immediately — this MUST succeed before we do anything else
        # Note: password is NOT stored in DB (no password column) — kept in MT5 manager memory only
        balance = 0.0
        existing = supabase_client.table('accounts').select('*').eq('login', request.login).execute()
        if existing.data and len(existing.data) > 0:
            supabase_client.table('accounts').update({
                'server': request.server,
                'status': 'pending',
                'password': request.password,
            }).eq('login', request.login).execute()
            logger.info(f"✅ Account {request.login} updated in database (pending MT5 verify)")
        else:
            supabase_client.table('accounts').insert({
                'login': request.login,
                'server': request.server,
                'status': 'pending',
                'balance': 0,
                'password': request.password,
            }).execute()
            logger.info(f"✅ Account {request.login} saved to database (pending MT5 verify)")
        
        # Confirm it was actually saved
        verify_save = supabase_client.table('accounts').select('id').eq('login', request.login).execute()
        if not verify_save.data:
            raise HTTPException(status_code=500, detail="Failed to save account to database. Please try again.")

        # Step 2: Register in MT5 manager
        mt5_manager.add_account(request.login, request.password, request.server)

        # Step 3: Try MT5 verify with 10s timeout (shorter — MT5 may be busy)
        mt5_verified = False
        try:
            connected = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: mt5_manager.connect_account(request.login, max_retries=1)
                ),
                timeout=10.0
            )
            if connected:
                account_info = mt5_manager.get_account_info(request.login)
                if account_info:
                    balance = float(account_info.balance)
                    mt5_verified = True
                    # Update DB with live balance and active status
                    supabase_client.table('accounts').update({
                        'status': 'active',
                        'balance': balance
                    }).eq('login', request.login).execute()
        except asyncio.TimeoutError:
            logger.warning(f"MT5 verify timed out for {request.login} — saved to DB, will connect on restart")
        except Exception as mt5_err:
            logger.warning(f"MT5 verify failed for {request.login}: {mt5_err} — saved to DB")

        # Notify auto-trader to reload watchlist
        try:
            from backend.services.auto_trader import get_auto_trader_instance
            instance = get_auto_trader_instance()
            if instance and instance.is_running:
                asyncio.create_task(instance.load_watchlist())
        except Exception as e:
            logger.warning(f"Could not notify auto-trader: {e}")

        if mt5_verified:
            return {
                "status": "success",
                "message": f"Account {request.login} connected and verified",
                "login": request.login,
                "server": request.server,
                "balance": balance,
                "verified": True
            }
        else:
            return {
                "status": "pending",
                "message": f"Account {request.login} saved. MT5 is busy — it will connect automatically on next restart.",
                "login": request.login,
                "server": request.server,
                "balance": 0,
                "verified": False
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to register account {request.login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect-account")
async def disconnect_account(request: DisconnectAccountRequest):
    """Disconnect/Unlink an MT5 account — removes from DB entirely"""
    try:
        login = request.login
        logger.info(f"🔓 Disconnecting account {login}...")

        # Remove from MT5 manager (in-memory, immediate)
        mt5_manager.remove_account(login)

        # DELETE from Supabase completely — so it won't reload on restart
        supabase_client.table('accounts').delete().eq('login', login).execute()
        logger.info(f"✅ Account {login} deleted from database")

        # Notify auto-trader to stop monitoring this account immediately
        try:
            from backend.services.auto_trader import get_auto_trader_instance
            instance = get_auto_trader_instance()
            if instance and instance.is_running:
                keys_to_remove = [k for k in instance.enabled_symbols if k.startswith(f"{login}_")]
                for k in keys_to_remove:
                    instance.enabled_symbols.pop(k, None)
                logger.info(f"Removed {len(keys_to_remove)} symbols from auto-trader for account {login}")
        except Exception as e:
            logger.warning(f"Could not notify auto-trader: {e}")

        return {
            "status": "success",
            "message": f"Account {login} disconnected and removed",
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

