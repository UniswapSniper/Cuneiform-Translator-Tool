# Deployment Guide

This guide covers deploying the Cuneiform Translator frontend and backend to production.

## Architecture Overview

- **Frontend**: React + Vite app deployed on Vercel (CDN + auto-preview URLs)
- **Backend**: Flask + Socket.IO deployed on a WebSocket-capable host (Render, Fly, Railway, etc.)
- **Database**: PostgreSQL or SQLite (data persistence)
- **CI/CD**: GitHub Actions runs tests and builds on every push/PR

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account linked to your GitHub repo
- Frontend source code in `/frontend`

### Steps

1. **Connect GitHub repo to Vercel**
   - Go to https://vercel.com/new
   - Select your GitHub repository (`cuneiform-translator-tool`)
   - Vercel should auto-detect Vite + React framework

2. **Configure Vercel Project Settings**
   - **Framework Preset**: Vite
   - **Project Root**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm ci`

3. **Add Environment Variables** (Settings > Environment Variables)
   
   For both **Preview** and **Production** environments:
   ```
   VITE_API_URL = https://<your-backend-domain>/api
   VITE_SOCKET_URL = wss://<your-backend-domain>
   ```
   
   Example (when backend is on render.com):
   ```
   VITE_API_URL = https://cuneiform-api.onrender.com/api
   VITE_SOCKET_URL = wss://cuneiform-api.onrender.com
   ```

4. **Deploy**
   - Merge code to `main` branch
   - Vercel auto-deploys within seconds
   - Preview URLs created for every PR

## Backend Deployment

### Option 1: Render (Recommended for WebSocket + Database)

1. **Create a Render account** at https://render.com

2. **Create a New Web Service**
   - Connect GitHub
   - Select repository `cuneiform-translator-tool`
   - Build Command: `pip install -e . && pip install gunicorn python-socketio`
   - Start Command: `gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:$PORT backend.app:app`
   - (For Flask + SocketIO, use eventlet worker)

3. **Configure Environment Variables**
   ```
   FLASK_ENV = production
   SECRET_KEY = <generate-a-random-string>
   JWT_SECRET_KEY = <generate-another-random-string>
   DATABASE_URL = postgresql://<user>:<password>@<host>:5432/<db>
   CORS_ORIGINS = https://cuneiform-translator-tool.vercel.app,https://cuneiform-translator-tool-*.vercel.app
   SOCKETIO_ASYNC_MODE = threading
   SOCKETIO_MESSAGE_QUEUE = (leave empty for single instance or set Redis URL)
   ```

4. **Create Database** (if using PostgreSQL)
   - Render: Create PostgreSQL database in dashboard
   - Use the connection string for `DATABASE_URL`
   - After first deploy, run migrations (if needed)

5. **Deploy**
   - Service auto-deploys from `main` branch
   - Get public URL (e.g., `cuneiform-api.onrender.com`)

### Option 2: Fly.io (Alternative)

1. **Create Fly account** and install `flyctl`
   ```bash
   brew install flyctl
   flyctl auth login
   ```

2. **Create app**
   ```bash
   cd cuneiform-translator-tool
   flyctl launch --name cuneiform-api
   ```
   - Region: closest to users
   - Choose PostgreSQL add-on

3. **Configure `fly.toml`**
   ```toml
   [env]
     FLASK_ENV = "production"
     SECRET_KEY = "your-secret-here"
     JWT_SECRET_KEY = "jwt-secret-here"
     CORS_ORIGINS = "https://cuneiform-translator-tool.vercel.app"
     SOCKETIO_ASYNC_MODE = "threading"
   ```

4. **Deploy**
   ```bash
   flyctl deploy
   ```

### Option 3: DigitalOcean App Platform / AWS / GCP
Similar flow — ensure platform supports:
- Long-lived WebSocket connections
- Persistent storage or attached database
- Environment variable injection

---

## Post-Deployment Verification

### 1. Test Backend Health
```bash
curl https://<backend-domain>/api/health
# Should return: {"status": "ok", "message": "...", "version": "1.0.0"}
```

### 2. Test Frontend
- Open https://cuneiform-translator-tool.vercel.app
- Open browser DevTools Console (F12)
- Should show `Socket connected` or no WebSocket errors
- Test a page that makes an API call (e.g., Analytics)

### 3. Test WebSocket Connection
- From frontend, navigate to Dashboard
- Click "Start WebSocket Test"
- Should see `✓ Connected` and receive test events

### 4. Verify CORS
- Check browser Console for CORS errors
- If present, ensure `CORS_ORIGINS` in backend includes the Vercel domain

---

## Environment Variables Reference

### Backend (Flask + SocketIO)

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| `FLASK_ENV` | `production` | ✓ | Set to `production` for prod |
| `SECRET_KEY` | random-string | ✓ | Change from default; use `os.urandom(24).hex()` |
| `JWT_SECRET_KEY` | random-string | ✓ | For JWT auth; use `os.urandom(24).hex()` |
| `DATABASE_URL` | `postgresql://...` | ✓ | Connection string; defaults to SQLite |
| `CORS_ORIGINS` | `https://example.vercel.app` | ✓ | Comma-separated; include all frontend domains |
| `SOCKETIO_MESSAGE_QUEUE` | `redis://...` | ✗ | For multi-instance; omit for single instance |
| `SOCKETIO_ASYNC_MODE` | `threading` | ✗ | Default: threading; use `gevent` if available |

### Frontend (Vercel)

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| `VITE_API_URL` | `https://api.example.com/api` | ✓ | Backend API base URL |
| `VITE_SOCKET_URL` | `wss://api.example.com` | ✓ | Backend WebSocket URL (wss for secure) |

---

## Troubleshooting

### "CORS error" in browser
- Backend `CORS_ORIGINS` doesn't include frontend domain
- Add frontend URL to backend environment variables
- Re-deploy backend

### "WebSocket connection failed"
- Backend domain doesn't support WebSockets or firewall blocks port
- Verify backend logs: `curl https://<backend>/api/health`
- Check Render/Fly/hosting provider allows WebSocket connections

### "Database connection refused"
- `DATABASE_URL` is wrong or DB is down
- Test connection string locally: `psql $DATABASE_URL`
- Ensure DB is in same region or network

### "502 Bad Gateway" after deploy
- Backend crashed on startup
- Check logs: Render dashboard > Logs or `fly logs`
- Common causes: missing deps, env var typo, port binding

---

## Local Development (for comparison)

If you want to run locally for testing before deployment:

```bash
# Terminal 1: Backend
source .venv/bin/activate
pip install -e .
FLASK_ENV=development python backend/run.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Access: http://localhost:5173
```

---

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`) automatically:
1. Runs unit tests (`pytest`) on Python 3.9, 3.10, 3.11
2. Lints Python code (`ruff`, `black`, `mypy`)
3. Builds and type-checks frontend (`npm run build`, `npm run type-check`)
4. Creates preview URL on PR (Vercel integration)
5. Deploys to production on merge to `main`

**To verify locally:**
```bash
pytest -q
npm run build
npm run lint
```

---

## Next Steps

1. Deploy backend to Render (or your choice platform)
2. Set Vercel environment variables to point to your backend
3. Merge to `main` — Vercel auto-deploys
4. Verify `/api/health` and WebSocket connection work
5. Test core flows in production (pipeline start, metrics, logs)

For questions or issues, check logs or reach out!
