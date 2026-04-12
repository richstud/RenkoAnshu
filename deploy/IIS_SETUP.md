# Renko Trading Bot - IIS Setup Guide for Windows VPS

## Overview
Using IIS (Internet Information Services) to host the frontend and reverse proxy to the backend API.

## Prerequisites
- Windows Server 2016 or later
- IIS installed with URL Rewrite module
- Frontend built: `npm run build`
- Backend running on http://localhost:8000

## Installation Steps

### 1. Install IIS with Required Modules
```powershell
# Run as Administrator

# Install IIS
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -All

# Install URL Rewrite Module (required for reverse proxy)
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite
# Or use Web Platform Installer
```

### 2. Create IIS Website

1. Open **Internet Information Services (IIS) Manager**
2. Right-click **Sites** > Select **Add Website**
3. Configure:
   - **Site name:** RenkoTrading
   - **Physical path:** `C:\Renko\frontend\dist`
   - **Binding:**
     - Type: http
     - IP: All Unassigned
     - Port: 80
     - Host name: (leave empty or enter domain)

### 3. Configure URL Rewrite for Backend Proxy

1. Double-click **URL Rewrite** on website
2. Click **Add Rule(s)...** > Select **Reverse Proxy**
3. Enter: `localhost:8000` > Click **OK**
4. Edit the rule:
   - Name: `ReverseProxyRule`
   - Pattern: `^api/(.*)`
   - Rewrite URL: `http://localhost:8000/api/{R:1}`
   - Check: **Append query string**

### 4. Configure index.html Fallback

1. In **URL Rewrite**, click **Add Rule(s)...** > **Blank rule**
2. Configure:
   - Name: `ReactRouter`
   - Pattern: `.*`
   - Conditions:
     - Add: `{REQUEST_FILENAME}` is not a file
     - Add: `{REQUEST_FILENAME}` is not a directory
   - Action:
     - Type: Rewrite
     - URL: `/index.html`

### 5. Enable Compression

1. Go to **HTTP Response Headers**
2. Check response compression is enabled
3. For performance, compress static assets

### 6. Set MIME Types

Add these MIME types if missing:
- `.woff` → `application/font-woff`
- `.woff2` → `application/font-woff2`
- `.json` → `application/json`

**Path:** MIME Types in IIS Manager

## Manual URL Rewrite XML (Alternative)

Create or edit `C:\Renko\frontend\dist\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <!-- Reverse Proxy for API -->
        <rule name="ReverseProxyRule" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://localhost:8000/api/{R:1}" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
            <set name="HTTP_X_FORWARDED_PROTO" value="http" />
            <set name="HTTP_X_FORWARDED_HOST" value="{HTTP_HOST}" />
          </serverVariables>
        </rule>
        
        <!-- React Router fallback -->
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
    
    <staticContent>
      <mimeMap fileExtension=".woff" mimeType="application/font-woff" />
      <mimeMap fileExtension=".woff2" mimeType="application/font-woff2" />
    </staticContent>
    
    <httpCompression>
      <staticCompression enabled="true" />
      <dynamicCompression enabled="true" />
    </httpCompression>
  </system.webServer>
</configuration>
```

## SSL Certificate Setup (HTTPS)

### Using Let's Encrypt (Automatic)

1. Install **Certbot for IIS**: https://certbot.eff.org/instructions
2. Run: `certbot certonly --iis -d yourdomain.com`
3. Certbot auto-binds to IIS

### Using IIS Self-Signed (Testing Only)

1. Open IIS Manager
2. Click server name > **Server Certificates**
3. Create **Self-Signed Certificate**
4. Edit site binding to use HTTPS + certificate

## DNS Configuration

Add DNS A record pointing to VPS IP:
```
yourdomain.com  A  <VPS_IP>
www.yourdomain.com  CNAME  yourdomain.com
```

## Windows Firewall

```powershell
# Allow HTTP/HTTPS
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 80
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 443

# Block Backend from internet
New-NetFirewallRule -DisplayName "Block Backend" -Direction Inbound -Action Block -Protocol TCP -LocalPort 8000
```

## Performance Tuning

1. **Enable HTTP/2:**
   - Edit binding > Enable HTTP/2

2. **Set App Pool Settings:**
   - Right-click **App Pools** > Edit:
     - Auto-recycle: 1740 minutes
     - Max workers: 4
     - Queue length: 1000

3. **Configure Output Caching:**
   - Add caching rules for static files (*.js, *.css, *.woff2)
   - Set expiration: 30 days for versioned files

4. **Enable Gzip Compression:**
   - Already configured in web.config above

## Monitoring

### View IIS Logs
```powershell
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log" -Tail 50 -Wait
```

### Monitor Backend Connection
```powershell
netstat -ano | findstr :8000
```

### Performance Monitoring
- App pool worker processes
- HTTP requests/sec
- Response time
- Queue length

## Troubleshooting

### 404 on API Calls
- Verify backend is running: http://localhost:8000/api/tickers
- Check URL Rewrite rules are enabled
- Review IIS logs for details

### React Routes Don't Work
- Ensure ReactRouter rewrite rule is in place
- Check rule order (React fallback must be last)
- Test: http://yoursite/settings (should show index.html)

### Slow Performance
- Reduce app pool recycle time
- Increase queue length
- Enable compression (already done)
- Check backend logs for slow queries

### SSL Certificate Issues
- Verify certificate is valid: `certbot certificates`
- Check renewal: `certbot renew --dry-run`
- Update IIS binding to use new certificate

## Startup Configuration

To auto-start IIS with Windows:

```powershell
# Already automatic, but verify:
Set-Service W3SVC -StartupType Automatic
Start-Service W3SVC

# Verify status:
Get-Service W3SVC
```

## Comparison: IIS vs Direct Server

| Aspect | IIS | Direct Port |
|--------|-----|------------|
| Setup | 10 min | 1 min |
| SSL/HTTPS | ✅ Easy | ⚠️ Manual |
| Proxy | ✅ Built-in | ❌ Need Nginx |
| Job Control | ✅ App Pools | ⚠️ Process |
| Enterprise | ✅ Yes | ❌ No |
| Performance | ✅ Optimized | ⚠️ Medium |

## Testing

1. **Homepage Load:**
   - http://yourdomain.com should show Renko UI

2. **API Proxy:**
   - http://yourdomain.com/api/tickers should return JSON

3. **React Routing:**
   - http://yourdomain.com/settings should work
   - http://yourdomain.com/positions should work

4. **Dashboard Functions:**
   - View accounts
   - See live prices
   - Create watchlist

## Next Steps

1. Configure DNS and get domain
2. Setup SSL certificate
3. Point domain to VPS
4. Test from external network
5. Monitor performance
6. Setup backups

---

**Last Updated:** April 12, 2026
