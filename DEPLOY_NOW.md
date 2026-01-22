# Backend Deployment Checklist (Render)

**Estimated time: 15-20 minutes**

## Pre-Deployment (Do Now)

- [ ] Verify local setup works (backend on :5001, frontend on :5173)
- [ ] Push all changes to GitHub (`main` branch)
  ```bash
  git add .
  git commit -m "Add Render deployment config and docs"
  git push origin main
  ```

## Deployment Steps (Render)

1. **Go to https://render.com**
   - Sign up / Login with GitHub
   - Connect your GitHub account

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select repository: `cuneiform-translator-tool`
   - Branch: `main`

3. **Configure Service**
   - Name: `cuneiform-api`
   - Region: `us-west-1` (or closest to you)
   - Runtime: `Python 3.9`
   - Build Command: 
     ```
     pip install -r backend/requirements.txt && pip install gunicorn python-socketio[client] eventlet
     ```
   - Start Command:
     ```
     cd backend && gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:$PORT --timeout 120 --access-logfile - "app:create_app('production')"
     ```
   - Instance Type: `Standard`

4. **Add Environment Variables** (click "Add From File" or paste manually):
   ```
   FLASK_ENV=production
   CORS_ORIGINS=https://cuneiform-translator-tool.vercel.app,https://cuneiform-translator-tool-*.vercel.app
   SOCKETIO_ASYNC_MODE=threading
   PYTHONUNBUFFERED=1
   ```
   - Render auto-generates `SECRET_KEY` and `JWT_SECRET_KEY`

5. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `cuneiform-db`
   - Database: `cuneiform_translator`
   - User: `cuneiform`
   - Region: Same as web service
   - Plan: `Free` (testing) or `Starter+` (production)

6. **Deploy**
   - Render auto-deploys from your `main` branch
   - Wait 3-5 minutes for build to complete
   - Status will show "Live" when ready

## Post-Deployment (Immediate)

- [ ] Test backend health:
  ```bash
  curl https://cuneiform-api.onrender.com/api/health
  ```
  Should return: `{"status": "ok", ...}`

- [ ] Get your backend URL (e.g., `https://cuneiform-api.onrender.com`)

- [ ] Update Vercel environment variables:
  - Go to https://vercel.com/dashboard
  - Select `cuneiform-translator-tool` project
  - Settings → Environment Variables
  - Update:
    ```
    VITE_API_URL = https://cuneiform-api.onrender.com/api
    VITE_SOCKET_URL = wss://cuneiform-api.onrender.com
    ```
  - Redeploy frontend (or commit to trigger auto-deploy)

- [ ] Test end-to-end:
  - Open https://cuneiform-translator-tool.vercel.app
  - Check browser console for WebSocket connection
  - Verify no CORS errors

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check Render Logs tab for errors; likely startup issue |
| CORS error in browser | Add Vercel domain to `CORS_ORIGINS` in Render env vars |
| WebSocket won't connect | Ensure `VITE_SOCKET_URL` points to correct Render domain |
| Database won't start | Wait a few minutes; PostgreSQL takes time to initialize |

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for detailed troubleshooting.

## Monitoring

- **Logs:** Render dashboard → Web Service → Logs (real-time)
- **Metrics:** Render dashboard → Web Service → Metrics (CPU, memory, requests)
- **Database:** Render dashboard → PostgreSQL → Logs

## Success! 🎉

You now have:
- ✅ Backend running on Render (`cuneiform-api.onrender.com`)
- ✅ Frontend on Vercel (`cuneiform-translator-tool.vercel.app`)
- ✅ PostgreSQL database connected
- ✅ CI workflow auto-running on GitHub
- ✅ Ready to start translating!
