# Complete Setup Guide

## 🎯 Quick Start

### 1. PostgreSQL Setup

**Option A: Docker (Easiest)**
```powershell
docker run --name ai-safety-db -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=ai_safety -p 5432:5432 -d postgres:16
```

**Option B: Local Installation**
1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Create database:
   ```sql
   CREATE DATABASE ai_safety;
   ```

**Option C: Cloud (Free)**
- Use Render.com or Supabase free tier
- Copy connection string

### 2. Environment Variables

Create `.env` file at project root:
```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_safety

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# LLM Providers
OPEN_AI_API_KEY=your-openai-key
GROK_API_KEY=your-groq-key
DEEPSEEK_API_KEY=your-deepseek-key
GEMINI_API_KEY=your-gemini-key
COHERE_AI_API_KEY=your-cohere-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Backend Setup

```powershell
# Navigate to backend
cd backend

# Install dependencies (already done)
# pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start API server
python -m uvicorn app.main:app --reload
# OR use the run script:
# .\run.ps1
```

**Important**: Always run uvicorn from the `backend` directory!

### 4. Frontend Setup

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (requires Node.js)
npm install

# Start development server
npm run dev
```

### 5. Access the Platform

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Troubleshooting

### SQLAlchemy Error (Python 3.13)
✅ **Fixed**: Updated SQLAlchemy to 2.0.45

### Module Not Found Error
**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Run uvicorn from `backend` directory:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### PostgreSQL Connection Error
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Test connection: `psql -U postgres -d ai_safety`

### Frontend Not Connecting to Backend
1. Check backend is running on port 8000
2. Check CORS_ORIGINS includes http://localhost:3000
3. Verify API URL in `frontend/src/lib/api.ts`

## 📋 Checklist

- [ ] PostgreSQL installed/running
- [ ] Redis installed/running (optional for now)
- [ ] .env file created with API keys
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Backend running (`python -m uvicorn app.main:app --reload` from backend/)
- [ ] Frontend dependencies installed (`npm install` in frontend/)
- [ ] Frontend running (`npm run dev` in frontend/)

## 🚀 Next Steps

1. Test the API: Visit http://localhost:8000/docs
2. Test the frontend: Visit http://localhost:3000
3. Try scanning a prompt: Use the "Scan Prompt" page
4. Check audit logs: View in "Audit Logs" page

## 📚 Documentation

- Backend setup: `backend/SETUP.md`
- PostgreSQL setup: `backend/POSTGRESQL_SETUP.md`
- Frontend setup: `FRONTEND_SETUP.md`
- Architecture: `docs/ARCHITECTURE.md`

