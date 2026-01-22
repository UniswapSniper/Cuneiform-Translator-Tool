# Local Development Setup

Quick reference for running Cuneiform Translator locally during development.

## Prerequisites

- Python 3.9+
- Node.js 18+
- macOS / Linux / Windows (with WSL)

## One-Time Setup

### Clone & Install

```bash
cd /path/to/cuneiform-translator-tool
source .venv/bin/activate  # or create: python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

### Verify Setup

```bash
# Test backend imports
python -c "from app import create_app; print('✓ Backend OK')"

# Test frontend build
cd frontend && npm run build && cd ..
echo "✓ Frontend OK"
```

## Running Locally

### Terminal 1: Backend (Flask + SocketIO)

```bash
source .venv/bin/activate
python backend/run.py
```

Output should show:
```
2026-01-22 12:00:00,000 INFO sqlalchemy.engine.Engine BEGIN (implicit)
...
 * Debugger is active!
 * Debugger PIN: XXX-XXX-XXX
```

**Endpoints:**
- API: http://localhost:5001/api
- Health: http://localhost:5001/api/health
- WebSocket: ws://localhost:5001

### Terminal 2: Frontend (Vite dev server)

```bash
cd frontend
npm run dev
```

Output should show:
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Access:** http://localhost:5173

### Test the Connection

1. Open http://localhost:5173 in browser
2. Check browser Console (F12) for WebSocket connection
3. Navigate to Dashboard and click "Start WebSocket Test"
4. Should see ✓ Connected and incoming events

## Running Tests

```bash
# All tests
pytest -q

# Specific test file
pytest tests/test_sample.py -v

# With coverage
pytest --cov=src --cov-report=html
```

## Code Quality

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint
ruff check .

# Type check
mypy src --ignore-missing-imports

# TypeScript
cd frontend && npm run type-check
```

## Frontend Only Development

If backend is already running and you just need frontend:

```bash
cd frontend
npm run dev
# Vite will proxy API calls to http://localhost:5001/api
```

## Environment Variables (Development)

Backend uses sensible defaults for local dev:
- `FLASK_ENV=development` (debug mode on)
- `DATABASE_URL=sqlite:///cuneiform_translator.db` (local SQLite)
- `SECRET_KEY=dev-secret-key-change-in-production`
- `CORS_ORIGINS=http://localhost:5173`

To override:
```bash
export FLASK_ENV=development
export DATABASE_URL=postgresql://user:pass@localhost/cuneiform
python backend/run.py
```

## Common Issues

### Port 5001 already in use
```bash
lsof -i :5001
kill -9 <PID>
python backend/run.py
```

### Port 5173 already in use
```bash
cd frontend
npm run dev -- --port 5174
```

### WebSocket connection fails
- Ensure backend is running on port 5001
- Check browser Console for CORS errors
- Verify `CORS_ORIGINS` includes frontend URL

### Module not found errors
```bash
pip install -e ".[dev]"
cd frontend && npm install
```

### Tests fail with "No module named pytest"
```bash
pip install -e ".[dev]"
```

## Database Migrations

If you modify `backend/app/models/`:

```bash
# Create new database (SQLite)
rm cuneiform_translator.db 2>/dev/null || true
python backend/run.py  # Starts with fresh schema

# For PostgreSQL, use Alembic (not yet configured)
```

## Stopping Services

```bash
# Kill backend
pkill -f "backend/run.py"

# Kill frontend dev server
# Ctrl+C in Terminal 2
```

## Production vs Development

| Aspect | Development | Production |
|--------|-------------|------------|
| Debug Mode | On | Off |
| Database | SQLite (local) | PostgreSQL (remote) |
| CORS | localhost:5173 | Vercel domain |
| SocketIO Queue | None (threading) | Redis (distributed) |
| SSL | No | Yes (wss://) |
| Auto-reload | Yes | No |

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Next: Run the Pipeline

Once backend + frontend are running locally:

```bash
# Terminal 3: Start a pipeline job
curl -X POST http://localhost:5001/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{"name": "test-run", "params": {"num_tablets": 10}}'

# Watch real-time updates in Frontend UI (Analytics page)
```

## Useful Commands

```bash
# Fresh rebuild
rm -rf frontend/node_modules frontend/.vite
cd frontend && npm ci && npm run build

# Backend health check
curl http://localhost:5001/api/health | python -m json.tool

# WebSocket test
curl -X POST http://localhost:5001/api/test/websocket/ping \
  -H "Content-Type: application/json" \
  -d '{"run_id": 1, "event_type": "progress", "data": {"progress": 50}}'

# View database
sqlite3 cuneiform_translator.db ".schema"
```

Happy hacking! 🚀
