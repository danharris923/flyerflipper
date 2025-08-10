# 🗺️ Vercel Google Maps Debug Guide

## Problem Analysis
Google Maps works in Docker (local) but not on Vercel (production).

### Current Architecture
- **Vercel Frontend** (your-app.vercel.app) → **Railway Backend** (flyerflipper-production.up.railway.app)
- **Docker Local** → Local Backend (localhost:8000)

## Likely Causes & Solutions

### 1. 🔑 Railway Missing Google API Key
**Check:** Railway environment variables don't have `GOOGLE_API_KEY`

**Solution:**
```bash
# In Railway dashboard, add environment variable:
GOOGLE_API_KEY=AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4
```

### 2. 🌐 Google API Key Domain Restrictions
**Check:** Google Cloud Console API key restrictions

**Solution:**
1. Go to [Google Cloud Console API & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click your API key: `AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4`
3. Under "Application restrictions" → "HTTP referrers (web sites)"
4. Add these domains:
   ```
   your-app-name.vercel.app/*
   *.vercel.app/*
   flyerflipper-production.up.railway.app/*
   localhost:*/*
   ```

### 3. 🔄 CORS Configuration
**Check:** Railway backend CORS doesn't allow Vercel domain

**Update backend/main.py:**
```python
# Add Vercel domain to CORS origins
cors_origins = [
    "https://your-app-name.vercel.app",
    "https://*.vercel.app",
    "https://flyerflipper-production.up.railway.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000"
]
```

### 4. 📍 Frontend Environment Variables
**Check:** Vercel environment variables

**Add to Vercel Dashboard:**
```bash
VITE_API_BASE_URL=https://flyerflipper-production.up.railway.app/api
VITE_GOOGLE_MAPS_API_KEY=AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4
```

## Quick Debug Commands

### Test Railway API Directly
```bash
curl https://flyerflipper-production.up.railway.app/api/status
```

### Test Vercel App API Connection
```bash
# Open browser dev tools on your Vercel app
# Check Network tab for failed API calls
# Look for CORS errors in Console
```

### Test Google APIs
```bash
curl "https://flyerflipper-production.up.railway.app/api/stores?postal_code=K1A0A6"
```

## Step-by-Step Fix

1. **Railway Environment Variables**
   - Login to Railway dashboard
   - Go to your project settings
   - Add `GOOGLE_API_KEY=AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4`

2. **Google Cloud Console**
   - Update API key restrictions to include your Vercel domain
   - Ensure these APIs are enabled:
     - Places API (New)
     - Geocoding API  
     - Maps JavaScript API

3. **Vercel Environment Variables**
   - Add API base URL pointing to Railway
   - Add Google Maps API key if frontend needs it

4. **Test & Verify**
   - Deploy changes
   - Test postal code entry on Vercel app
   - Check browser dev tools for errors

## Expected Result
After fixes, both environments should work:
- ✅ Docker: `localhost:3000` → `localhost:8000` (with Google Maps)
- ✅ Vercel: `your-app.vercel.app` → `railway.app/api` (with Google Maps)