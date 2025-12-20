# Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- LLM API keys (OpenAI, Claude, Gemini, DeepSeek, Groq, Cohere)

## Installation

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database**
```bash
# Create database
createdb ai_safety

# Run migrations
alembic upgrade head
```

6. **Start Redis**
```bash
redis-server
```

7. **Run the application**
```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest tests/ -v
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

See `render.yaml` for Render deployment configuration.

