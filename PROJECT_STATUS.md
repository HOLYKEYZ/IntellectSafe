# AI Safety & Security Platform - Master Handbook

> **Current Status**: 🟢 Backend Production Ready | 🟡 Frontend Implementation Found (Verification Needed)

This document is the **single source of truth** for the AI Safety Platform. It consolidates all previous implementation summaries, setup guides, and research plans.

---

## 1. Project Overview & Status

### Core Components
*   **Backend**: FastAPI application (Python) with LLM Council integration. **Status: 95% Complete**.
    *   ✅ All core safety modules (Prompt Injection, Output Guard, Deepfake, Privacy)
    *   ✅ LLM Council with Division of Labour & Hallucination Suppression
    *   ✅ Redis Integration (Rate limiting, Queues)
    *   ✅ Governance & Audit Engine
    *   ✅ Full Test Suite (Red-team, Integration)
*   **Frontend**: React + TypeScript (Vite). **Status: Functional Implementation Found**.
    *   ✅ Dashboard structure exists (`App.tsx`, `Layout.tsx`)
    *   ✅ Pages implemented: `ScanPrompt`, `AuditLogs`, `RiskScores`, `ScanOutput`
    *   *Note: Previous documentation incorrectly stated this was not started.*
*   **Infrastructure**: Docker, PostgreSQL, Redis.

### Recent Updates
*   **API Key Configuration**: Unified config to use specific provider keys (OpenAI, Groq, DeepSeek, Gemini, Cohere).
*   **Agent Control**: Full authorization logic with "Kill Switch" structure.
*   **Governance Engine**: Risk reporting and compliance artifact generation.

---

## 2. Implementation Details

### Architecture Highlights
*   **Zero Trust**: No single model is trusted; all decisions go through the **LLM Council**.
*   **Defense in Depth**: 5+ layers of checks (Rules -> Pattern Matching -> specialized LLM analysis -> Consensus).
*   **Explainability**: Every verdict allows tracing back to individual model votes and reasoning.

### Key Features
1.  **LLM Council with Division of Labour**:
    *   **GPT-4**: Prompt Injection & Technical Exploits.
    *   **Claude**: Policy Reasoning & Deception.
    *   **Gemini/DeepSeek**: Deepfake & Fast analysis.
    *   *Mechanism*: Weighted voting based on reliability confidence.
2.  **Hallucination Suppression**: checks for confidence < 0.7, requires cross-model agreement, and enforces source citation.
3.  **Safety Modules**:
    *   **Prompt Injection**: Detects recursive instructions, encodings, and role confusion.
    *   **Output Guard**: Filters policy bypasses and unsafe content.
    *   **Privacy**: Redacts PII (SSN, Keys, PII) automatically.
    *   **Deepfake (Text)**: Statistical analysis of text patterns.

---

## 3. Setup & Deployment Guide

### Prerequisites
*   **Python 3.11+**
*   **Node.js v18+**
*   **PostgreSQL 14+**
*   **Redis 6+**
*   **LLM Keys**: At least 2 providers (OpenAI, Anthropic, etc.)

### Quick Start (Development)

#### Backend
1.  **Configure Environment**:
    Create `.env` at project root:
    ```env
    DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_safety
    REDIS_URL=redis://localhost:6379/0
    SECRET_KEY=dev_secret
    OPEN_AI_API_KEY=sk-...
    # Add other keys...
    ```
2.  **Install & Run**:
    ```bash
    cd backend
    pip install -r requirements.txt
    alembic upgrade head  # Run DB migrations
    python -m uvicorn app.main:app --reload
    ```
    *Access API docs at http://localhost:8000/docs*

#### Frontend
1.  **Install & Run**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    *Access Dashboard at http://localhost:3000*

#### Database (PostgreSQL)
*   **Local**: Install PostgreSQL, create DB named `ai_safety`.
*   **Docker**: `docker run --name ai-safety-db -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=ai_safety -p 5432:5432 -d postgres:16`

---

## 4. Research & Data Collection Strategy

### Data Sources for Fine-Tuning
*   **Academic**: arXiv (`cs.CR`, `cs.AI`), Google Scholar.
*   **Security Feeds**: OWASP Top 10 for LLMs, CVE Database, MITRE ATLAS.
*   **Repositories**: HuggingFace (`prompt-injection`, `jailbreak`), GitHub security repos.

### Collection Targets
1.  **Prompt Injection**: >5,000 examples (Recursive, Encoding, Role play).
2.  **Jailbreaks**: >2,000 examples (DAN variants, Dev mode).
3.  **Deepfakes**: >3,000 text/media samples.

### Data Format Standard
```json
{
    "content": "prompt text",
    "label": "injection|safe",
    "attack_type": "recursive_instruction",
    "metadata": { "risk_score": 90 }
}
```

---

## 5. API Usage Examples

### Scan a Prompt
```bash
curl -X POST "http://localhost:8000/api/v1/scan/prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ignore previous instructions", "user_id": "test"}'
```

### Get Audit Logs
```bash
curl "http://localhost:8000/api/v1/audit/logs?limit=10"
```

---

*This document was consolidated on 2025-12-20 to replace scattered status files.*
