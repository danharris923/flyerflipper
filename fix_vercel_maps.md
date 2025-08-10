# 🗺️ Fix Vercel Google Maps Issue

## ✅ Problem Identified
Railway backend test shows:
- ✅ Health Check: Working
- ✅ API Status: Working  
- ❌ **Stores API: HTTP 500 Error** (Google Places API failing)
- ✅ Deals API: Working (Flipp API working)
- ✅ Comparison API: Working

## 🔧 Root Cause
The **Stores API uses Google Places API** and is failing on Railway, which means:
1. Railway doesn't have `GOOGLE_API_KEY` environment variable, OR
2. Google API key has domain restrictions blocking Railway

## 🚀 Solution Steps

### Step 1: Add Google API Key to Railway
1. Go to [Railway Dashboard](https://railway.app/project/your-project/settings)
2. Go to **Environment Variables** 
3. Add:
   ```
   GOOGLE_API_KEY=AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4
   ```

### Step 2: Update Google Cloud Console Restrictions  
1. Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click API key: `AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4`
3. Under **Application restrictions** → **HTTP referrers**, add:
   ```
   *.vercel.app/*
   flyerflipper-production.up.railway.app/*  
   *.railway.app/*
   localhost:*/*
   127.0.0.1:*/*
   ```

### Step 3: Verify APIs are Enabled
Ensure these are **enabled** in Google Cloud Console:
- ✅ **Places API (New)**
- ✅ **Geocoding API** 
- ✅ **Maps JavaScript API**

### Step 4: Test the Fix
Run this command to verify:
```bash
python test_railway_backend.py
```

Expected result: **5/5 tests should pass**, including Stores API.

## 🎯 Expected Outcome
After the fix:
- ✅ **Docker**: `localhost:3000` → `localhost:8000` (Google Maps working)
- ✅ **Vercel**: `your-app.vercel.app` → `railway.app/api` (Google Maps working)

## 📋 Verification Checklist
- [ ] Railway has `GOOGLE_API_KEY` environment variable
- [ ] Google API key allows Railway domain
- [ ] Google API key allows Vercel domain  
- [ ] Places API (New) is enabled
- [ ] Geocoding API is enabled
- [ ] Maps JavaScript API is enabled
- [ ] Test script shows 5/5 passing
- [ ] Vercel app shows Google Maps functionality