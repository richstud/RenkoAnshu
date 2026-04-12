# IIS Frontend Hosting on VPS (114.29.239.50)

**How to host the React frontend on your Windows VPS for internet access**

## 📦 Step 1: Build Frontend

### On Your Local Machine
```powershell
cd C:\Renko\frontend
npm run build
```

This creates: `frontend/dist/` (production build)

### Copy to VPS
Upload `frontend/dist/` to VPS at:
```
C:\Renko\frontend\dist\
```

**Or build directly on VPS:**
```powershell
# On VPS
cd C:\Renko\frontend
npm run build
```

---

## 🌐 Step 2: Setup IIS on VPS

### Install IIS
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -All
```

### Install URL Rewrite Module
1. Download: https://www.iis.net/downloads/microsoft/url-rewrite
2. Install on VPS

---

## 📝 Step 3: Configure IIS Website

### Create Website Entry
1. Open **IIS Manager**
2. Right-click **Sites** → **Add Website**
3. Configure:
   - **Site name:** RenkoTrading
   - **Physical path:** `C:\Renko\frontend\dist`
   - **Type:** http
   - **Port:** 80
   - **Host name:** (leave empty)

---

## 🔀 Step 4: URL Rewrite Rules

### Auto-Setup with web.config
Create `C:\Renko\frontend\dist\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <!-- Reverse Proxy API to Backend -->
        <rule name="APIProxy" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://localhost:8000/api/{R:1}" />
        </rule>
        
        <!-- React Router Fallback -->
        <rule name="ReactRouter" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

### Manual IIS Configuration
1. In IIS Manager, select **RenkoTrading** site
2. Double-click **URL Rewrite**
3. **Add Rule** → **Reverse Proxy**
4. Enter: `localhost:8000`
5. Modify pattern to: `^api/(.*)`
6. Set rewrite URL to: `http://localhost:8000/api/{R:1}`

---

## 🔐 Step 5: HTTPS/SSL (Optional)

### Using Let's Encrypt (Recommended)
```powershell
# Install Certbot for IIS
choco install certbot-iis -y

# Generate certificate
certbot certonly --iis -d yourdomain.com

# Auto-configures IIS
```

### Using Self-Signed (Testing)
1. IIS Manager → Server Certificates
2. Create Self-Signed Certificate
3. Update binding to use HTTPS + certificate

---

## 📡 Step 6: DNS Setup

### Point Domain to VPS
1. Buy domain (GoDaddy, Namecheap, etc.)
2. Add DNS A record:
   ```
   yourdomain.com  A  114.29.239.50
   ```
3. Wait 5-10 minutes for DNS propagation

### Test DNS
```powershell
nslookup yourdomain.com
```
Should return: **114.29.239.50**

---

## ✅ Verification Checklist

- [ ] Frontend built: `npm run build`
- [ ] Build output in: `C:\Renko\frontend\dist\`
- [ ] IIS website created and running
- [ ] URL Rewrite rules configured
- [ ] API proxy working to backend
- [ ] React routing working (no 404s)
- [ ] DNS pointing to VPS
- [ ] SSL certificate installed (optional)
- [ ] Firewall allows port 80/443

---

## 🧪 Test Access

### Before DNS Propagates
```powershell
# On VPS or from your machine
curl http://114.29.239.50
```

Should return HTML of React app.

### After DNS Ready
```
http://yourdomain.com
```

Should load trading dashboard.

### Test API Proxy
```
http://yourdomain.com/api/tickers
```

Should return JSON data.

---

## 🔧 Troubleshooting

### 404 on React Routes
- Verify ReactRouter rewrite rule is in web.config
- Restart IIS: `iisreset.exe`

### API Calls Failing
- Verify backend running on localhost:8000
- Check firewall allows localhost:8000
- View IIS logs: `C:\inetpub\logs\LogFiles\W3SVC1\`

### HTTPS Not Working
- Verify certificate installed
- Check binding uses correct certificate
- Test with: `https://yourdomain.com`

### DNS Not Resolving
- Check A record in domain registrar
- Wait 5-10 minutes
- Clear DNS cache: `ipconfig /flushdns`

---

## 🚀 Final URL

After setup, access your app at:

```
https://yourdomain.com
```

Or directly via IP (during testing):

```
http://114.29.239.50
```

---

## 📞 Quick Checklist

```powershell
# Step 1: Build
npm run build

# Step 2: Deploy to IIS
# Copy dist/ to C:\Renko\frontend\dist\

# Step 3: Create web.config above at dist root

# Step 4: Create IIS website pointing to dist/

# Step 5: Test
# http://114.29.239.50

# Step 6: Add domain DNS

# Step 7: Access
# https://yourdomain.com
```

---

**Your VPS IP:** 114.29.239.50  
**Backend:** Running on port 8000  
**Ready to deploy!** 🎉
