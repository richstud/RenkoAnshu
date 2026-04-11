"""
API endpoints for MT5 account management (link/unlink accounts)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["accounts"])

# Import MT5 manager and Supabase
from backend.mt5.connection import mt5_manager
from backend.supabase.client import supabase_client


class ConnectAccountRequest(BaseModel):
    login: int
    password: str
    server: str


@router.post("/connect-account")
async def connect_account(request: ConnectAccountRequest):
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
        
         # Save to Supabase (without password for security)
        try:
            # Check if already exists
            existing = supabase_client.table('accounts').select('*').eq('login', request.login).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update
                supabase_client.table('accounts').update({
                    'server': request.server,
                    'status': 'active',
                    'balance': float(account_info.balance)
                }).eq('login', request.login).execute()
                
                logger.info(f"✅ Account {request.login} updated in database")
            else:
                # Insert new (NO PASSWORD STORED for security)
                supabase_client.table('accounts').insert({
                    'login': request.login,
                    'server': request.server,
                    'status': 'active',
                    'balance': float(account_info.balance)
                }).execute()
                
                logger.info(f"✅ Account {request.login} added to database")
        
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
