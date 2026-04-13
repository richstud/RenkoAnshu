# 📍 FILE LOCATION GUIDE

## 🎯 Quick Navigation

### For Deployment to VPS

**Copy this file from local to VPS:**
```
FROM: E:\Renko\backend\api\endpoints.py
TO:   c:\tradingbot\renko\backend\api\endpoints.py
```

### For Building Frontend

**Build from this location:**
```
cd E:\Renko\frontend
npm run build
```

---

## 📂 Complete File Structure

### Frontend Files (E:\Renko\frontend\src\)

#### New Component
```
✨ E:\Renko\frontend\src\components\TradeHistory.tsx
   - Purpose: Display trades by date + export to CSV
   - Lines: 175
   - Status: NEW - Add this file if missing
```

#### Modified Components
```
✏️ E:\Renko\frontend\src\components\RenkoChart.tsx
   - Changes: Canvas sizing fix for crosshair visibility
   - Lines changed: ~15
   - Lines: 137-157 (canvas dimension handling)
   - Lines: 516-520 (canvas element styling)

✏️ E:\Renko\frontend\src\components\WatchlistManager.tsx
   - Changes: Better error handling on delete
   - Lines changed: ~18
   - Lines: 79-98 (handleDelete function)

✏️ E:\Renko\frontend\src\App.tsx
   - Changes: Import TradeHistory component
   - Lines changed: ~3
   - Line: 6 (import statement added)
   - Lines: 230-233 (component added to UI)
```

### Backend Files (For VPS)

#### Modified Endpoint File
```
✏️ c:\tradingbot\renko\backend\api\endpoints.py
   (Same as: E:\Renko\backend\api\endpoints.py)
   
   Changes: Add 2 new endpoints + Query import
   Lines changed: ~70
   
   - Line 8: Add Query to imports
   - Lines 399-440: New get_trades_by_date endpoint
   - Lines 485-549: New export_trades endpoint
```

---

## 📋 Checklist: What Files to Update

### Local Machine (E:\Renko) - Already Done ✅

**Frontend - Check these files:**
- [ ] ✏️ `frontend/src/components/RenkoChart.tsx` - Has canvas sizing fix
- [ ] ✏️ `frontend/src/components/WatchlistManager.tsx` - Has delete improvements
- [ ] ✨ `frontend/src/components/TradeHistory.tsx` - File exists (NEW)
- [ ] ✏️ `frontend/src/App.tsx` - Has TradeHistory import

**Backend - To Deploy to VPS:**
- [ ] ✏️ `backend/api/endpoints.py` - Has 2 new endpoints + Query import

### VPS (c:\tradingbot\renko) - Next Steps

**Backend - Need to Deploy:**
- [ ] Copy `endpoints.py` from local to VPS
- [ ] Verify file copied successfully
- [ ] Restart backend service

---

## 🔍 Verification: Files Are Correct

### Local: Verify RenkoChart.tsx
Line 516 should have: `className="w-full h-full bg-slate-950 cursor-crosshair block"`

### Local: Verify WatchlistManager.tsx
Line 82 should have: `const url =`

### Local: Verify TradeHistory.tsx
Line 1 should have: `import { useEffect, useState } from 'react';`

### Local: Verify App.tsx
Line 6 should have: `import TradeHistory from './components/TradeHistory';`
Line 231 should have: `{selectedAccount && (`

### VPS: Verify endpoints.py
Line 8 should have: `from fastapi import APIRouter, HTTPException, Query`
Line 399 should have: `@router.get("/trades/by-date/{account_id}")`
Line 485 should have: `@router.get("/trades/export/{account_id}")`

---

## 📦 Summary of Changes

### Total Files Modified: 4
```
E:\Renko\frontend\src\components\RenkoChart.tsx
E:\Renko\frontend\src\components\WatchlistManager.tsx
E:\Renko\frontend\src\App.tsx
E:\Renko\backend\api\endpoints.py (← Also on VPS)
```

### Total Files Created: 1
```
E:\Renko\frontend\src\components\TradeHistory.tsx
```

### Total Size Impact: ~300 lines

---

## 🚀 Deployment Files

### Frontend Build (After npm run build)
```
E:\Renko\frontend\dist\
├── index.html
├── assets\
│   ├── index-xxxxx.js (main app)
│   └── style-xxxxx.css
└── ... (static assets)
```
**Action:** Copy entire `dist/` folder contents to your web server

### Backend Deployment
```
Source: E:\Renko\backend\api\endpoints.py
Destination: c:\tradingbot\renko\backend\api\endpoints.py
Action: Copy file, then restart backend service
```

---

## 📝 Documentation Files (For Reference)

All in `E:\Renko\`:
```
📖 DEPLOYMENT_GUIDE_FIXES.md - Detailed deployment guide
📖 STEP_BY_STEP_DEPLOYMENT.md - Step-by-step instructions
📖 QUICK_REFERENCE_CARD.md - Developer reference
📖 FIXES_APPLIED_SUMMARY.md - Quick overview
📖 DEPLOYMENT_CHECKLIST.md - Testing checklist
📖 IMPLEMENTATION_COMPLETE.md - Final summary
📖 FILE_LOCATION_GUIDE.md - This file
```

---

## 🎯 Quick Deployment Commands

### Frontend Build
```bash
cd E:\Renko\frontend
npm run build
# Output: dist/ folder created
```

### Backend Restart (on VPS)
```bash
# Stop service
taskkill /F /IM python.exe

# Start service
cd c:\tradingbot\renko
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Test Backend
```bash
# From local machine
curl http://vps-ip:8000/api/trades/by-date/101510620?date_str=2026-04-13
```

---

## ⚠️ Critical Files

**DO NOT DELETE:**
- [ ] `E:\Renko\frontend\src\components\TradeHistory.tsx` (new component)
- [ ] `E:\Renko\backend\api\endpoints.py.backup` (on VPS - rollback)

**MUST UPDATE:**
- [ ] `E:\Renko\backend\api\endpoints.py` (copy to VPS)
- [ ] `E:\Renko\frontend/` (build with npm)

---

## 🔄 Rollback Files

If something goes wrong:
```
VPS: c:\tradingbot\renko\backend\api\endpoints.py.backup
Local: git checkout HEAD -- frontend/src/
```

---

## ✅ Final Checklist

### Before Deployment
- [ ] All local files updated ✅
- [ ] Backend file ready to copy ✅
- [ ] Documentation complete ✅

### During Deployment
- [ ] Frontend built successfully
- [ ] Backend file copied to VPS
- [ ] Backend service restarted
- [ ] No errors in console

### After Deployment
- [ ] Crosshair visible on chart
- [ ] Watchlist delete works
- [ ] Trade history loads
- [ ] CSV export downloads

---

## 📞 If You Get Lost

1. **Check file locations:** This guide shows where everything is
2. **Follow deployment guide:** STEP_BY_STEP_DEPLOYMENT.md
3. **Use testing guide:** DEPLOYMENT_CHECKLIST.md
4. **Review quick reference:** QUICK_REFERENCE_CARD.md

---

**You have all the files you need. Follow STEP_BY_STEP_DEPLOYMENT.md next!**
