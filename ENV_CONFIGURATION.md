# Environment Configuration Guide

## Required .env Variables

Create a `.env` file at the project root (`AI-safety/.env`)

### 🔴 Required (No Defaults - Must Set)

```env
# PostgreSQL Database Connection
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_safety_db

# Security Secret Key (for JWT tokens, API keys, etc.)
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key-here-minimum-32-characters
```

### 🟡 Optional (Have Defaults - Recommended to Set)

```env
# Redis Connection (default: redis://localhost:6379/0)
REDIS_URL=redis://localhost:6379/0

# CORS Origins (default: http://localhost:3002)
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:3002

# Environment (default: production)
ENVIRONMENT=development

# Debug Mode (default: False)
DEBUG=true
```

### 🟢 API Keys (You Already Have These)

```env
# OpenAI
OPEN_AI_API_KEY=sk-proj-NS7EYMa5pnMl0dZG...hjpxTXut-o2ifVOoBMNv0EA

# Grok (xAI)
GROK_API_KEY=gsk_mEpZvqWd2akmmTuqoikp...Iem8jTlGksjoHBhaDbMJo2c

# DeepSeek
DEEPSEEK_API_KEY=sk-...5441b44a541e337fc6609a

# Google Gemini
GEMINI_API_KEY=AIzaSyCs5fI9qPBYngGOTDsIj2iF0KRg_9Pn67Y

# Cohere
COHERE_AI_API_KEY=kLa6NElWn8kSZd1n8dbQtY7XRPdObvswluG9x7zc
```

# Fallback Model (if using separate key)

# Currently not in config - may need to add if fallback uses different provider

FALLBACK_API_KEY=...

````

## How to Get Missing Values

### 1. DATABASE_URL

**Option A: Install PostgreSQL Locally**
1. Download: https://www.postgresql.org/download/
2. Install with default settings
3. Create database:
   ```powershell
   # Using psql
   psql -U postgres
   CREATE DATABASE ai_safety_db;
   CREATE USER ai_safety_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_safety_db TO ai_safety_user;
````

4. Format: `postgresql://ai_safety_user:your_password@localhost:5432/ai_safety_db`

**Option B: Use Docker**

```powershell
docker run -d --name postgres-ai-safety -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=ai_safety_db -p 5432:5432 postgres:15
```

Format: `postgresql://postgres:your_password@localhost:5432/ai_safety_db`

**Option C: Use Cloud Database (Render, Supabase, etc.)**

- Get connection string from provider
- Format: `postgresql://user:pass@host:port/db`

### 2. SECRET_KEY

**Generate with Python:**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Or with OpenSSL (Linux/Mac):**

```bash
openssl rand -hex 32
```

**Or use online generator:**

- https://randomkeygen.com/ (use "CodeIgniter Encryption Keys")

**Minimum length:** 32 characters (64 hex characters recommended)

### 3. REDIS_URL

**Option A: Install Redis Locally**

- Windows: https://github.com/microsoftarchive/redis/releases
- Linux: `sudo apt-get install redis-server`
- Mac: `brew install redis`

**Option B: Use Docker**

```powershell
docker run -d --name redis-ai-safety -p 6379:6379 redis:latest
```

**Default:** `redis://localhost:6379/0` (already in code, no need to set if using default)

### 4. CORS_ORIGINS

**If frontend runs on:**

- `http://localhost:3000` → Set: `CORS_ORIGINS=http://localhost:3000`
- Multiple origins → Set: `CORS_ORIGINS=http://localhost:3000,http://localhost:3002`
- Production → Set: `CORS_ORIGINS=https://yourdomain.com`

**Default:** `http://localhost:3002` (already in code)

## Complete .env Example

```env
# ============================================
# REQUIRED - Must Set
# ============================================
DATABASE_URL=postgresql://postgres:mySecurePassword123@localhost:5432/ai_safety_db
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# ============================================
# API KEYS
# ============================================
OPEN_AI_API_KEY=sk-proj-NS7EYMa5pnMl0dZG...hjpxTXut-o2ifVOoBMNv0EA
GROK_API_KEY=gsk_mEpZvqWd2akmmTuqoikp...Iem8jTlGksjoHBhaDbMJo2c
DEEPSEEK_API_KEY=sk-...5441b44a541e337fc6609a
GEMINI_API_KEY=AIzaSyCs5fI9qPBYngGOTDsIj2iF0KRg_9Pn67Y
COHERE_AI_API_KEY=kLa6NElWn8kSZd1n8dbQtY7XRPdObvswluG9x7zc

# ============================================
# OPTIONAL - Recommended
# ============================================
ENVIRONMENT=development
DEBUG=true
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

## Verification

After setting up `.env`, verify it works:

```powershell
cd backend
python -c "from app.core.config import get_settings; s = get_settings(); print('✅ Config loaded successfully')"
```

If you see errors about missing fields, check:

1. `.env` file is at project root (not in `backend/`)
2. All required variables are set
3. No typos in variable names
4. Values don't have extra quotes (unless needed)

## Security Notes

- ⚠️ **Never commit `.env` to git** (should be in `.gitignore`)
- ⚠️ **SECRET_KEY** should be unique and random
- ⚠️ **DATABASE_URL** contains password - keep secure
- ⚠️ **API keys** are sensitive - don't share
