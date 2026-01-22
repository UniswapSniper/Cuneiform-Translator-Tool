# Cuneiform Translator Backend

Flask + SQLAlchemy + SocketIO API for the Cuneiform Translator pipeline.

## Features

- 🚀 RESTful API with Flask blueprints
- 🔗 Real-time WebSocket communication with Socket.IO
- 💾 SQLAlchemy ORM with SQLite database
- 🔐 JWT authentication ready
- 📊 Database models for pipelines, models, tablets, users
- 🎯 Modular blueprint architecture

## Project Structure

```
backend/
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration management
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── pipeline.py
│   │   ├── model.py
│   │   └── tablet.py
│   ├── api/                # API blueprints
│   │   ├── health.py       # Health check endpoints
│   │   ├── pipeline.py     # Pipeline control endpoints
│   │   ├── models.py       # Model management endpoints
│   │   ├── tablets.py      # Tablet gallery endpoints
│   │   └── analytics.py    # Analytics endpoints
│   ├── websocket/          # WebSocket handlers
│   │   └── __init__.py
│   └── utils/              # Utility functions
│       └── __init__.py
├── run.py                  # Development server
├── requirements.txt        # Dependencies
└── README.md

## Setup

1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start development server:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - API health status
- `GET /api/health/ready` - Readiness probe

### Pipeline Management
- `GET /api/pipeline/status` - List all pipeline runs
- `GET /api/pipeline/<id>` - Get pipeline details
- `POST /api/pipeline/start` - Start new pipeline
- `POST /api/pipeline/<id>/cancel` - Cancel running pipeline
- `GET /api/pipeline/<id>/steps` - Get pipeline steps

### Model Management
- `GET /api/models` - List models
- `GET /api/models/<id>` - Get model details
- `PUT /api/models/<id>` - Update model
- `DELETE /api/models/<id>` - Delete model
- `POST /api/models/compare` - Compare models

### Tablet Gallery
- `GET /api/tablets` - List tablets
- `GET /api/tablets/<id>` - Get tablet details
- `POST /api/tablets/<id>/annotations` - Add annotation
- `PUT /api/tablets/annotations/<id>` - Update annotation
- `DELETE /api/tablets/annotations/<id>` - Delete annotation

### Analytics
- `GET /api/analytics/summary` - Overall summary
- `GET /api/analytics/pipeline/stats` - Pipeline statistics
- `GET /api/analytics/models/stats` - Model statistics
- `GET /api/analytics/tablets/stats` - Tablet statistics

## WebSocket Events

### Subscribe/Unsubscribe
- `subscribe:pipeline` - Subscribe to pipeline updates
- `unsubscribe:pipeline` - Unsubscribe from pipeline

### Updates
- `pipeline:update` - Pipeline progress update
- `step:update` - Step progress update
- `metrics:update` - Training metrics update

## Database

SQLite database is created automatically in the app directory. Schema includes:

- **users** - User accounts with authentication
- **pipeline_runs** - Pipeline execution history
- **pipeline_steps** - Individual step records
- **trained_models** - Trained ML models
- **tablets** - Cuneiform tablet records
- **annotations** - Region annotations

## Technologies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-SocketIO** - WebSocket support
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - CORS support
- **SQLAlchemy** - Database toolkit
- **Werkzeug** - WSGI utilities
