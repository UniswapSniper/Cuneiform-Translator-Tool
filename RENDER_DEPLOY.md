# Render Deployment Guide for Cuneiform Translator Backend

## Prerequisites

- GitHub account with `cuneiform-translator-tool` repository
- Render account (https://render.com) — sign up with GitHub
- Vercel frontend already deployed

## Step-by-Step Deployment to Render

### 1. Connect GitHub to Render

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Select "Deploy existing repository" 
4. Connect your GitHub account and select `cuneiform-translator-tool`
5. Choose repository: `cuneiform-translator-tool`

### 2. Configure Web Service

**Basic Settings:**
- Name: `cuneiform-api`
- Region: Select closest to your users (e.g., `us-west` or `us-east`)
- Branch: `main`
- Runtime: `Python 3.9`
- Build Command:
  ```
  pip install -r backend/requirements.txt && pip install gunicorn python-socketio[client] eventlet
  ```
- Start Command:
  ```
  cd backend && gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:$PORT --timeout 120 --access-logfile - "app:create_app('production')"
  ```
- Instance Type: `Standard` (adequate for early stages)

### 3. Add Environment Variables

In Render dashboard, go to "Environment":

```
FLASK_ENV = production
SECRET_KEY = (Render will auto-generate if left empty, or paste a random string)
JWT_SECRET_KEY = (Render will auto-generate if left empty, or paste a random string)
CORS_ORIGINS = https://cuneiform-translator-tool.vercel.app,https://cuneiform-translator-tool-*.vercel.app
SOCKETIO_ASYNC_MODE = threading
PYTHONUNBUFFERED = 1
```

**Note:** Don't set `DATABASE_URL` yet; we'll create the database next.

### 4. Create PostgreSQL Database (Connected to Service)

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `cuneiform-db`
3. Database: `cuneiform_translator`
4. User: `cuneiform`
5. Region: Same as web service
6. Pricing Plan: `Free` (for testing) or `Starter+` (for production)
7. Click "Create Database"

Once created:
- Render will auto-populate `DATABASE_URL` in the web service env vars
- Database will initialize on first deploy

### 5. Deploy

1. Back to web service settings
2. Click "Deploy latest commit" or just push to `main`
3. Render will:
   - Pull code from GitHub
   - Install dependencies
   - Build and start the service
   - Allocate a public URL (e.g., `https://cuneiform-api.onrender.com`)

**Deployment takes 3-5 minutes.** You can watch logs in real-time.

### 6. Verify Deployment

Once deployed (Status: "Live"):

```bash
# Test health endpoint
curl https://cuneiform-api.onrender.com/api/health

# Should return:
# {"status": "ok", "message": "...", "version": "1.0.0"}
```

**Note:** First request may take 10-15 seconds if the service is spinning up.

### 7. Update Vercel Environment Variables

Now that your backend is deployed, update Vercel frontend env vars:

1. Go to Vercel dashboard → `cuneiform-translator-tool` project
2. Settings → Environment Variables
3. Update (or create):
   ```
   VITE_API_URL = https://cuneiform-api.onrender.com/api
   VITE_SOCKET_URL = wss://cuneiform-api.onrender.com
   ```
4. Redeploy frontend (or just merge to `main` to trigger auto-deploy)

### 8. Test End-to-End

1. Open https://cuneiform-translator-tool.vercel.app
2. Open browser Console (F12)
3. Should see "Socket connected" or no WebSocket errors
4. Navigate to Dashboard or Analytics
5. Test WebSocket connection (if test endpoint exists)

---

## Monitoring & Logs

### View Logs
- Render dashboard → Web Service → Logs
- Real-time logs shown; can download for debugging

### Common Issues

| Issue | Fix |
|-------|-----|
| 502 Bad Gateway | Check Logs tab; likely startup error. Verify `DATABASE_URL` is set. |
| CORS error | Add Vercel domain to `CORS_ORIGINS` env var and redeploy. |
| WebSocket timeout | Increase `--timeout` in gunicorn start command. |
| Database won't connect | Verify `DATABASE_URL` is correct; check PostgreSQL is running. |

### Scale Up (if needed)
- Render dashboard → Web Service → Instance Type
- Upgrade from `Free` or `Standard` to higher tier
- Takes ~1 minute to scale; app doesn't go down

---

## Environment Variable Generation (for manual setup)

If you need to generate secrets locally:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Then paste into Render env vars.

---

## Database Management

### Backup & Restore
- Render automatically backs up PostgreSQL daily (free tier: 7-day retention)
- Paid plans: longer retention
- Restore from dashboard if needed

### Connect Locally (for debugging)
```bash
# Get DATABASE_URL from Render
# Format: postgresql://user:password@host:port/database

psql "postgresql://user:password@host:port/database"
```

---

## Auto-Deploy from GitHub

- **Push to `main`:** Render auto-deploys
- **Push to other branches:** Skipped (unless configured)
- **Cancel deploy:** Render dashboard → Deployments → Cancel
- **Rollback:** Deploy → Redeploy a previous commit

---

## Cost Estimate (as of 2026)

| Component | Free Tier | Starter+ |
|-----------|-----------|----------|
| Web Service | $7/month (after free hours) | $12+/month |
| PostgreSQL | Free (limited) | $15+/month |
| **Total** | ~$7/month | ~$27+/month |

(Render's free tier gives monthly free compute hours; prices updated periodically)

---

## Next Steps After Deployment

1. ✅ Backend running on Render
2. ✅ Frontend on Vercel pointing to Render backend
3. [ ] Run full pipeline test in production
4. [ ] Monitor logs for errors
5. [ ] Set up alerts / monitoring (optional)
6. [ ] Scale database or compute if needed

---

## Support & Troubleshooting

**Render Support:** https://render.com/docs  
**Socket.IO + Gunicorn:** https://python-socketio.readthedocs.io  
**PostgreSQL:** https://www.postgresql.org/docs

For deployment-specific issues, check:
1. Render dashboard → Web Service → Logs
2. Render dashboard → PostgreSQL → Logs
3. GitHub → Actions (if using CI)
