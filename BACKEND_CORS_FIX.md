# Backend CORS Configuration Fix

## Problem
Your Vercel frontend (`https://cuneiform-translator-tool.vercel.app`) cannot connect to your Render backend because of CORS restrictions.

## Solution

### Step 1: Configure Render Backend Environment Variables

Go to your **Render Dashboard** → **cuneiform-translator-tool** service → **Environment** tab

Add/Update these environment variables:

```
CORS_ORIGINS=https://cuneiform-translator-tool.vercel.app,https://cuneiform-translator-tool-git-main-uniswapsniper.vercel.app
FLASK_ENV=production
SECRET_KEY=<generate-a-random-string>
```

### Step 2: Verify Render Service is Running

1. Go to Render dashboard
2. Check if your backend service is deployed and running
3. Note the backend URL (should be something like `https://cuneiform-translator-tool-xxxxx.onrender.com`)

### Step 3: Update Vercel Environment Variables

Go to **Vercel Dashboard** → **cuneiform-translator-tool** → **Settings** → **Environment Variables**

Add these (replace with your actual Render URL):

```
VITE_API_URL=https://your-backend.onrender.com/api
VITE_SOCKET_URL=https://your-backend.onrender.com
```

### Step 4: Redeploy Both Services

1. **Render**: Will auto-redeploy when you save environment variables
2. **Vercel**: Go to **Deployments** → Click **...** on latest → **Redeploy**

### Step 5: Test Connection

1. Wait 2-3 minutes for both services to redeploy
2. Visit `https://cuneiform-translator-tool.vercel.app`
3. Check console - should now show "Connected" status
4. WebSocket should connect successfully

## Alternative: Allow All Origins (Quick Test)

If you want to quickly test, you can temporarily set:

**Render Environment Variable:**
```
CORS_ORIGINS=*
```

This allows all origins (less secure, but good for testing).

## What Your Current Setup Looks Like

**Frontend (Vercel):**
- Deployed at: `https://cuneiform-translator-tool.vercel.app`
- Needs: `VITE_API_URL` and `VITE_SOCKET_URL` environment variables

**Backend (Render):**
- Likely at: `https://cuneiform-translator-tool-xxxxx.onrender.com`
- Needs: `CORS_ORIGINS` to include your Vercel URL
