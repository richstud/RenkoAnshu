# ⚡ QUICK SETUP: CREATE SUPABASE TABLES

## Your Supabase Project Info ✅
- **Project URL**: https://mflakcwgbpghyzdyevsb.supabase.co
- **Status**: ✅ Ready to add tables

---

## 3-STEP SETUP (Takes 2 minutes)

### Step 1: Open Supabase SQL Editor
1. Go to: https://app.supabase.com/project/mflakcwgbpghyzdyevsb/sql/new
2. Click "New Query" button (top right)

### Step 2: Copy the Schema SQL
1. In your repo, open: `backend/supabase/schema.sql`
2. Select ALL the code (Ctrl+A)
3. Copy it (Ctrl+C)

### Step 3: Execute in Supabase
1. Paste the entire SQL into the Supabase SQL Editor
2. Click the "RUN" button (or press Ctrl+Enter)
3. Wait for it to complete (should say "Success")

---

## What Will Be Created ✅

After running the schema, you'll have these tables:

```
✅ accounts           - Your MT5 trading accounts
✅ watchlist          - Symbols you're trading (with SL, TP, Trail)
✅ trades             - All executed trades
✅ logs               - Bot events and errors
✅ bot_control        - Bot on/off status per account
✅ settings           - Global settings (brick size, default SL/TP)
✅ price_ticks        - Real-time bid/ask prices
✅ available_symbols  - List of symbols with pip values
```

---

## Verify It Worked

After running, in Supabase:
1. Go to "Tables" (left sidebar)
2. You should see all 8 tables listed

If you see them → ✅ **You're done!**

---

## ❓ Troubleshooting

### Error: "Table already exists"
- This is OK! It means the table was created before.
- The SQL uses `IF NOT EXISTS` so it won't error.
- Just run the entire schema again if you want a fresh start.

### Error: "Permission denied"
- Make sure you're logged into Supabase
- Use your project link above (not a random project)

### No error but nothing happens
- Check if SQL pasted correctly
- Click "RUN" again
- Check "Results" tab at the bottom

### Still stuck?
- Contact Supabase support: https://supabase.com/support
- Or check the logs in Supabase dashboard

---

## Next Steps

Once tables are created:

1. ✅ Update your `.env` file with Supabase credentials:
```
SUPABASE_URL=https://mflakcwgbpghyzdyevsb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mbGFrY3dnYnBnaHl6ZHlldnNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU1Nzc3OTQsImV4cCI6MjA5MTE1Mzc5NH0.2Ev5gdEz-9rSgDkKTC_siX_SH5iEfFK6SPM8S8uRx9Q
```

2. ✅ Test connection locally:
```bash
python -c "from backend.supabase.client import supabase_client; print(supabase_client.table('accounts').select('*').execute())"
```

3. ✅ Ready for backend + frontend development!

---

## Direct Supabase Link
🔗 https://app.supabase.com/project/mflakcwgbpghyzdyevsb/sql/new

Open that link now and paste the schema! ⚡

