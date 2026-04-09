# INFORMATION NEEDED - BEFORE DEPLOYMENT

Please gather and provide these details to complete your setup. This checklist ensures your VPS deployment will work correctly.

---

## SECTION 1: VPS & INFRASTRUCTURE

### 1.1 VPS Specifications
- [ ] **VPS Address**: Enter IP or domain name
  - Example: `192.168.1.100` or `mytradingbot.com`
  - Value: __________________114.29.239.50_________________

- [ ] **VPS Operating System**: Windows or Linux?
  - [ ] Windows Server 2019/2022
  - [ ] Linux (Ubuntu 20.04/22.04)
  - [ ] Other: ___________________Microsoft Windows 10/2016/2019________________

- [ ] **VPS Username**: For connecting remotely
  - Value: ______________anxsriv173@gmail.com_____________________

- [ ] **VPS Password**: For connecting remotely
  - Value: __________________RichAnshu@1987_________________

- [ ] **VPS RAM Available**: How much RAM?
  - [Y] 2GB
  - [ ] 4GB
  - [ ] 8GB
  - [ ] 16GB+

- [ ] **VPS Storage Available**: How much disk space?
  - [Y] 20GB
  - [ ] 50GB
  - [ ] 100GB+

### 1.2 Network
- [ ] **VPS Port 8000 Accessible**: Can you reach backend from outside?
  - [ ] Yes (VPS firewall allows it)
  - [Y] No (need to configure)
  - [ ] Not sure

- [ ] **Domain Name** (optional, for production):
  - Value: ___________________________________
  - Note: Not required initially, can use IP address

- [ ] **SSH Key or Password**: For secure connection
  - [ ] SSH key (have it ready)
  - [ ] Password authentication (provide above)

---

## SECTION 2: METATRADER 5 (MT5) ACCOUNT

### 2.1 Broker Account
- [ ] **Broker Name**: Which broker are you using?
  - [Y] XM
  - [ ] HotForex
  - [ ] IC Markets
  - [ ] OANDA
  - [ ] Other: ___________________________________

- [ ] **Account Type**: Live or Demo?
  - [ ] Live (Real money)
  - [Y] Demo (Practice account)

- [ ] **Account Login Number**:
  - Value: __________101510620 _________________________
  - Note: 5-10 digit number from MT5 login screen

- [ ] **Account Password**:
  - Value: _____________RichAnshu@1987______________________
  - ⚠️ Keep this secure!

- [ ] **Server Name**:
  - Value: __________ XMGlobal-MT5 5_________________________
  - Note: Exact server name from MT5 login dropdown (e.g., "XM Real-3" or "OANDA-v20")
  - **How to find it**: 
    1. Open MT5
    2. Go to File → Login
    3. Look at the "Server" dropdown
    4. Copy the exact text

- [ ] **Account Balance** (approximately):
  - Value: $ _______10000____________________________

- [ ] **Leverage**: What leverage on your account?
  - [ ] 1:50
  - [ ] 1:100
  - [ ] 1:200
  - [ ] 1:500
  - [Y] Other: ___________________________________

### 2.2 Trading Symbols
- [ ] **Primary Symbol**: Main symbol to trade
  - Value: _______XAUUSD____________________________
  - Default: XAUUSD (Gold)

- [ ] **Available Symbols**: List all symbols you want to trade
  - [ ] XAUUSD (Gold)
  - [ ] EURUSD (EUR/USD)
  - [ ] GBPUSD (GBP/USD)
  - [ ] USDJPY (USD/JPY)
  - [Y] Others: _______ALL____________________________

- [ ] **Symbol Settings**: For each symbol, verify:
  - Example for XAUUSD:
    - Tick size: 0.01 ✓
    - Pip value: 0.01 ✓
    - Minimum lot: 0.01 ✓
    - Maximum lot: 100.0 ✓
  - **How to check**:
    1. In MT5, right-click symbol in Market Watch
    2. Select "Specifications"
    3. Note the Min/Step/Max values

- [ ] **Trading Hours**: When does the market trade?
  - [ ] 24/5 (Forex, Gold)
  - [ ] Specific hours: ___________________________________
  - [Y] Need to exclude weekends: Yes / No

---

## SECTION 3: TRADING PARAMETERS

### 3.1 Stop Loss (SL) & Take Profit (TP)

- [ ] **Default Stop Loss**: How many pips/points to lose before closing?
  - Value: _____ pips (default suggestion: 50 for XAUUSD)
  - Note: Can be changed per symbol later

- [ ] **Default Take Profit**: How many pips/points to gain before closing?
  - Value: _____ pips (default suggestion: 100 for XAUUSD)

- [ ] **Trailing Stop**: Use trailing stops to lock profits?
  - [ ] Yes, use trailing stops
  - [ ] No, fixed SL/TP only
  - If yes, how many pips to trail?
    - Value: _____ pips (default: 30-50)

### 3.2 Lot Sizing

- [ ] **Default Lot Size**: Fixed lot size per trade
  - [ ] 0.01 (micro lot)
  - [ ] 0.1 (mini lot)
  - [ ] 1.0 (standard lot)
  - [ ] Custom: _____ lots

- [ ] **Dynamic Lot Sizing**: Scale lot based on account balance?
  - [Y] Yes (increase lots as balance grows)
  - [ ] No (fixed lot always)
  - If yes, provide formula or breakpoints:
    - Balance < $500: 0.01 lots
    - Balance $500-$1000: 0.5 lots
    - Balance > $1000: 1.0 lots
    - (or your own rules): ___________________________________

- [ ] **Max Lot Size**: Absolute maximum per trade
  - Value: _____ lots

- [ ] **Max Concurrent Positions**: Maximum trades open at once
  - [ ] 1 position per symbol
  - [ ] 2-3 positions per symbol
  - [Y] Unlimited
  - Value: _____

### 3.3 Renko Strategy Parameters

- [ ] **Default Brick Size**: Renko brick size in pips
  - Value: _____ pips (default: 1.0)
  - Note: Can be changed from UI per symbol

- [ ] **Reversal Strategy**: How your bot trades
  - [ ] Renko reversals (current setup ✓)
  - [ ] Trend following
  - [ ] Scalping

- [ ] **Confirmation Signals** (optional):
  - [ ] None needed
  - [ ] Other indicators: ___________________________________

---

## SECTION 4: ACCOUNT & SECURITY

### 4.1 Supabase (Database)

- [ ] **Supabase Account**: Do you have one?
  - [ ] Already created (provide details below)
  - [ ] Need to create (I'll explain how)

If already created:
- [ ] **Supabase Project URL**:
  - Value: https://mflakcwgbpghyzdyevsb.supabase.co
  
- [ ] **Supabase Anon Key**:
  - Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q
  - ⚠️ Keep this secure! (But it's okay to share the anon key)

- [ ] **Supabase Service Role Key** (optional, for admin):
  - Value: eyJ... (long key)
  - ⚠️ NEVER SHARE THIS KEY!

### 4.2 Deployment Keys (You'll Create These)

- [ ] **MT5 Path on VPS**: Where is MT5 installed?
  - [ ] Windows: `C:\Program Files\MetaTrader 5`
  - [ y] Custom path: __"C:\Program Files\XM Global MT5\terminal64.exe"_________________________________

- [ ] **Backend Port**: What port for the API?
  - [ y] 8000 (default, recommended)
  - [ ] Custom: _____

- [ ] **Frontend Domain** (where will frontend run?):
  - [ ] On same VPS
  - [ ] Separate domain: ___________________________________
  - [y ] Vercel/Netlify: ___________________________________

---

## SECTION 5: RISK MANAGEMENT & RULES

### 5.1 Risk per Trade
- [ ] **Risk per Trade**: How much can you lose per trade?
  - [ ] 1% of account balance
  - [ ] 2% of account balance
  - [ ] Fixed $ amount: $___________
  - [ ] Fixed pips: _____ pips

- [ ] **Daily Loss Limit**: Stop trading if lost X per day?
  - [ ] Yes, limit: $___________
  - [ ] No limit

- [ ] **Daily Win Target**: Stop trading if won X per day?
  - [ ] Yes, target: $___________
  - [ ] No target

### 5.2 Time Controls

- [ ] **Trading Hours**: When should bot be active?
  - [ ] 24/5 (Monday-Friday always)
  - [ ] Specific hours: From _____ To _____ (server time)
  - [ ] Skip timezone: ___________________________________

- [ ] **Weekend Trading**:
  - [ ] Skip weekends completely
  - [ ] Trade Friday night to Sunday close
  - [ ] Trade 24/7

- [ ] **Holidays to Skip**:
  - [ ] List dates: ___________________________________

### 5.3 Emergency Controls

- [ ] **Max Account Drawdown**: Stop if account drops by X%?
  - [ ] Yes, limit: _____%
  - [ ] No limit

- [ ] **Auto-Stop Conditions**:
  - [ ] Stop if no MT5 connection
  - [ ] Stop if no internet
  - [ ] Stop if database unreachable
  - [ ] Other: ___________________________________

---

## SECTION 6: MONITORING & NOTIFICATIONS

### 6.1 Alerts (Email/Telegram notifications)

- [ ] **Email for Alerts**:
  - Value: ___________________________________
  - [ ] Alert on trade entry
  - [ ] Alert on SL hit
  - [ ] Alert on TP hit
  - [ ] Alert on errors

- [ ] **Telegram Bot** (optional):
  - [ ] Need Telegram notifications
  - [ ] Don't need
  - If yes, Telegram Chat ID: ___________________________________

### 6.2 Logging

- [ ] **Log Level**:
  - [ ] INFO (normal, recommended)
  - [ ] DEBUG (verbose)
  - [ ] WARNING (errors only)

- [ ] **Log Retention**: Keep logs for how long?
  - [y ] 7 days
  - [ ] 30 days
  - [ ] 90 days
  - [ ] Unlimited

---

## SECTION 7: MULTI-ACCOUNT SETUP (if applicable)

If you have multiple MT5 accounts:

### Account 1:
- [ ] **Login**: ___________________________________
- [ ] **Password**: ___________________________________
- [ ] **Server**: ___________________________________
- [ ] **Symbols to trade**: ___________________________________

### Account 2:
- [ ] **Login**: ___________________________________
- [ ] **Password**: ___________________________________
- [ ] **Server**: ___________________________________
- [ ] **Symbols to trade**: ___________________________________

### Account 3 (if more):
- [ ] **Login**: ___________________________________
- ...

---

## SECTION 8: DEPLOYMENT ENVIRONMENT

- [ ] **Environment Type**:
  - [ ] Development (local testing first)
  - [ ] Staging (testing on VPS)
  - [y ] Production (live trading)

- [ ] **Current Stage**: What stage are you at?
  - [ y] Just coded, never run yet
  - [ ] Tested locally on Windows
  - [ ] Ready to go live

- [ ] **Backup & Recovery**:
  - [ ] Need automated backups: Yes / No
  - [ ] Backup frequency: Daily / Weekly / Monthly

---

## QUICK COPY-PASTE TEMPLATE

**Copy and fill this for easy reference:**

```
=== DEPLOYMENT CHECKLIST ===

VPS: [IP/Domain]
MT5 Account: [Login]
MT5 Server: [Server]
MT5 Password: [Password]
Primary Symbol: [XAUUSD or other]
Supabase URL: [https://__.supabase.co]
Supabase Key: [key start]
Default SL: [50 pips]
Default TP: [100 pips]
Default Lot: [0.01]
Default Brick: [1.0 pips]
Trailing Stop: [Yes/No, pips]
Max Positions: [1 or more]
```

---

## Next Steps After Filling This

1. **Fill out this entire checklist**
2. **Create Supabase account** (if not done)
3. **Run /schema.sql** on Supabase
4. **Follow VPS_DEPLOYMENT_GUIDE.md** step by step
5. **Test everything** before going live

---

## Questions?

If you're unsure about any field:
- **Ask before proceeding**
- Don't guess - each value affects live trading!
- Better to take 1 hour for setup than lose money on wrong config

