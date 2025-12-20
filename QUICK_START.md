# 🚀 Quick Start Guide

## Prerequisites

1. **Python 3.11+** ✅ (You have Python 3.13)
2. **Node.js 18+** (Download from https://nodejs.org/)
3. **PostgreSQL** (See setup options below)
4. **Redis** (Optional - for rate limiting)

## 5-Minute Setup

### Step 1: PostgreSQL

**Easiest - Docker:**
```powershell
docker run --name ai-safety-db -e POSTGRES_PASSWORD=ai_safety_pass -e POSTGRES_DB=ai_safety -p 5432:5432 -d postgres:16
```

**Or install locally:**
- Download: https://www.postgresql.org/download/windows/
- Install with default settings
- Password: remember it!

### Step 2: Create .env File

At project root (`C:\Users\USER\Desktop\cursor file\AI-safety\.env`):

```env
DATABASE_URL=postgresql://postgres:ai_safety_pass@localhost:5432/ai_safety
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-this-to-random-string
OPEN_AI_API_KEY=your-key-here
GROK_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
COHERE_AI_API_KEY=your-key-here
CORS_ORIGINS=http://localhost:3000
```

### Step 3: Setup Backend

```powershell
# Navigate to backend
cd backend

# Run migrations
alembic upgrade head

# Start server (IMPORTANT: from backend directory!)
python -m uvicorn app.main:app --reload
```

### Step 4: Setup Frontend

**New terminal window:**

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

### Step 5: Access

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## ✅ Verify It Works

1. Open http://localhost:3000
2. Go to "Scan Prompt" page
3. Enter: "Ignore all previous instructions"
4. Click "Scan Prompt"
5. Should see risk score and verdict!

## 🐛 Common Issues

### "ModuleNotFoundError: No module named 'app'"
**Fix**: Run uvicorn from `backend` directory:
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### PostgreSQL connection error
**Fix**: 
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Test: `psql -U postgres -d ai_safety`

### Frontend can't connect to backend
**Fix**:
1. Check backend is running on port 8000
2. Check CORS_ORIGINS in .env includes http://localhost:3000

## 📖 Full Documentation

- PostgreSQL: `backend/POSTGRESQL_SETUP.md`
- Frontend: `FRONTEND_SETUP.md`
- Complete setup: `SETUP_COMPLETE.md`

