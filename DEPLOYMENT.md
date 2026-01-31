# Deployment Guide

## Backend → Render

### Prerequisites
- A [Render](https://render.com) account
- A PostgreSQL database (can be created on Render)

### Deployment Steps

1.  **Create a PostgreSQL Database on Render**
    - Dashboard → New → PostgreSQL
    - Copy the **Internal Database URL** after creation

2.  **Deploy the Backend**
    - Dashboard → New → Web Service
    - Connect your GitHub repo
    - **Root Directory**: `backend`
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3.  **Environment Variables** (Set in Render Dashboard → Environment)

    | Variable | Value |
    |---|---|
    | `DATABASE_URL` | `<Internal Postgres URL from Step 1>` |
    | `SECRET_KEY` | `<Generate a random 32+ char string>` |
    | `CORS_ORIGINS` | `https://your-frontend.vercel.app` |
    | `GEMINI_API_KEY` | `<Your Gemini API Key>` |
    | `GROQ_API_KEY` | `<Your Groq API Key>` |
    | `OPENROUTER_API_KEY` | `<Your OpenRouter API Key>` |

---

## Frontend → Vercel

### Prerequisites
- A [Vercel](https://vercel.com) account

### Deployment Steps

1.  **Deploy the Frontend**
    - Dashboard → Add New → Project
    - Import your GitHub repo
    - **Root Directory**: `frontend`
    - **Framework Preset**: Vite (auto-detected)
    - **Build Command**: `npm run build` (default)
    - **Output Directory**: `dist` (default)

2.  **Environment Variables** (Set in Vercel Dashboard → Settings → Environment Variables)

    | Variable | Value |
    |---|---|
    | `VITE_API_URL` | `https://your-backend.onrender.com/api/v1` |

---

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables (Local)
Create a `.env` file in the project root (`AI-safety/.env`):
```env
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=dev_secret_key_for_local_only
CORS_ORIGINS=http://localhost:5173
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
```
