# Account Manager - Link/Unlink MT5 Accounts

## What You Need to Link an Account

You need **BOTH**:
1. **Account Login Number** (e.g., 101510620)
2. **Account Password** (your MT5 password)

Plus the **Server** (e.g., ICMarkets, XM.MT5, etc.)

## New Frontend UI

A new **Account Manager** component has been added to the frontend dashboard that allows you to:

✅ **Link new MT5 accounts** - Add account login + password + server
✅ **View all connected accounts** - See status and balance
✅ **Unlink accounts** - Disconnect accounts when not needed

## How to Use

### Step 1: Access Account Manager
The Account Manager appears at the top of the dashboard after deployment.

### Step 2: Link Your 3 Accounts

For each account, enter:
- **Account Login Number**: Your MT5 account number
- **Password**: Your MT5 password  
- **Server**: Select from dropdown (ICMarkets, XM.MT5, etc.)
- Click **Link Account**

Example:
```
Account 1:
  Login: 101510620
  Password: ****
  Server: ICMarkets
  
Account 2:
  Login: 123456789
  Password: ****
  Server: ICMarkets
  
Account 3:
  Login: 987654321
  Password: ****
  Server: ICMarkets
```

### Step 3: Verify Connected
Once linked, accounts appear in "Connected Accounts" list with:
- ✅ Status (Active/Offline)
- 💰 Current Balance
- 🔓 Unlink button

## What Happens Behind the Scenes

1. **Backend receives login + password**
2. **Connects to MT5** using MT5 API
3. **Validates connection** - checks if credentials work
4. **Retrieves account info** - balance, equity, etc.
5. **Saves to Supabase** - stores in `accounts` table
6. **Auto-trader sees it** - immediately picks up for auto-trading

## Auto-Trading Now Works

Once 3 accounts are linked:

1. **Add BTCUSD to watchlist** for each account (in database or UI)
2. **Enable algo_enabled=true** for each
3. **Auto-trader loads them all**
4. **When signal triggers:**
   - Account 1 ($X balance) → Lot size calculated → Trade executed
   - Account 2 ($Y balance) → Lot size calculated → Trade executed
   - Account 3 ($Z balance) → Lot size calculated → Trade executed

All simultaneously with their own lot sizes! 🎉

## Files Created/Modified

### New Files:
- `frontend/src/components/AccountManager.tsx` - UI for linking/unlinking
- `backend/api/account_manager.py` - Backend endpoints for account management

### Modified Files:
- `frontend/src/App.tsx` - Added AccountManager import and component
- `backend/main.py` - Registered account_manager router

## API Endpoints

### Link Account
```
POST /api/connect-account
{
  "login": 101510620,
  "password": "your_password",
  "server": "ICMarkets"
}
```

### Unlink Account
```
POST /api/disconnect-account?login=101510620
```

### Get All Accounts
```
GET /api/accounts
```

### Get Specific Account
```
GET /api/account/101510620
```

## Deployment

```bash
cd E:\Renko

git add frontend/src/components/AccountManager.tsx \
        backend/api/account_manager.py \
        frontend/src/App.tsx \
        backend/main.py

git commit -m "Add account manager UI for linking/unlinking MT5 accounts"

git push origin main
```

On VPS:
```bash
cd /path/to/renko
git pull origin main
pkill -f "python -m backend.main"
python -m backend.main &
```

Frontend will hot-reload automatically!

## Security Note

⚠️ **Passwords are sent to backend** - make sure:
- Use HTTPS in production
- Don't share your credentials
- Passwords are stored only for connecting (not persisted unnecessarily)
- Use environment variables for default accounts

## Troubleshooting

### "Failed to connect to MT5 account"
- Check credentials (login/password) are correct
- Verify server name is correct
- Check internet connection to MT5 server

### Account shows "Offline"
- Account was disconnected
- Check MT5 terminal is running
- Verify credentials still valid

### Can't see AccountManager in UI
- Restart backend and frontend
- Check browser console for errors
- Verify files were deployed correctly
