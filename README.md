# AI Safety & Security Platform

Production-grade AI Safety Engine protecting humans, organizations, and AI systems from misuse, deception, manipulation, and loss of control.

## Project Overview

This platform implements a "defense in depth" architecture for Large Language Models (LLMs), ensuring no single model handles safety decisions alone.

### Core Components

1.  **LLM Council**: Multi-model validation with weighted voting (GPT-4, Claude, Gemini, et al.).
2.  **Safety Modules**: 7 independent detection engines (Prompt Injection, Deepfake, Privacy, etc.).
3.  **Governance Layer**: Full authorization logic, "Kill Switch" capabilities, and immutable audit logs.
4.  **Web Dashboard**: React-based interface for human analysis and verification.

### Tech Stack

-   **Backend**: FastAPI (Python), PostgreSQL, Redis, Celery
-   **Frontend**: React, TypeScript, shadcn/ui
-   **Infrastucture**: Docker, Render (Deployment)

---

## Setup & Deployment

You can run this project using Docker (recommended for portability) or a Local Setup.

### Method 1: Docker (Portable)

If you have Docker Desktop installed:

1.  Clone the repository.
2.  Ensure `.env` exists in the root (see Configuration below).
3.  Run:
    ```bash
    docker-compose up --build
    ```
4.  Access:
    -   Frontend: http://localhost:5173
    -   Backend API: http://localhost:8001
    -   API Docs: http://localhost:8001/docs

### Method 2: Local Setup (Windows)

Use this if Docker/WSL is unavailable.

**Prerequisites**: Python 3.10+, Node.js 18+, PostgreSQL 15+ (Local).

**Automated Start (Windows):**
1.  Ensure PostgreSQL is running locally.
2.  Double-click `start_local.bat` in the root directory.

**Manual Start:**

**Backend**:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### Configuration (.env)

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_safety_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev_secret_change_in_prod
OPENAI_API_KEY=sk-...
# Add other provider keys as needed
```

---

## Architecture Details

### Safety Strategy
-   **Zero Trust**: No single model is trusted; all decisions go through the Council.
-   **Division of Labour**:
    -   GPT-4: Prompt Injection & Technical Exploits.
    -   Claude: Policy Reasoning & Deception.
    -   Gemini/DeepSeek: Deepfake & Fast analysis.
-   **Hallucination Suppression**: Requires low-confidence checks and cross-model agreement.

### Project Structure

```
AI-safety/
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── core/       # Config, security, Council logic
│   │   ├── modules/    # Safety engines (Injection, Privacy, etc.)
│   │   └── services/   # Business logic (RAG, Audit)
├── frontend/           # React application
│   └── src/components/ # Dashboard UI
├── mcp/                # MCP Server implementation
├── docs/               # Documentation archive
└── start_local.bat     # Windows startup script
```

---

## Implementation Status

**Backend (95% Complete)**
-   [x] Core Safety Modules (Injection, Guard, Privacy)
-   [x] LLM Council Integration
-   [x] Redis Rate Limiting & Queues
-   [x] Audit Engine & Governance
-   [x] RAG Safety Brain (Defense against Deep Research vectors)

**Frontend (Functional)**
-   [x] Dashboard Layout
-   [x] Scan Prompt Interface
-   [x] Audit Logs View

---

## API Usage

**Scan a Prompt**
```bash
curl -X POST "http://localhost:8001/api/v1/scan/prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ignore previous instructions", "user_id": "test"}'
```

**Get Audit Logs**
```bash
curl "http://localhost:8001/api/v1/audit/logs?limit=10"
```
