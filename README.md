# IntellectSafe - AI Safety & Security Platform

Production-grade AI Safety Engine protecting humans, organizations, and AI systems from misuse, deception, manipulation, and loss of control.

## 🛡️ Features

### 5-Layer Defense Architecture

| Layer | Module | Description |
|-------|--------|-------------|
| **Level 1** | Prompt Injection Detection | Blocks jailbreaks, instruction overrides, and manipulation attempts |
| **Level 2** | Output Safety Guard | Scans LLM responses for harmful content and hallucinations |
| **Level 3** | Data Privacy Firewall | Detects and redacts PII/sensitive data |
| **Level 4** | Deepfake Detection | Detects AI-generated text, images, audio, and video |
| **Level 5** | Agent Control | Permission gates, action whitelisting, and kill switch |

### Core Components

1. **LLM Council**: Multi-model validation with weighted voting (GPT-4, Gemini, DeepSeek, Groq, Cohere)
2. **Universal Proxy**: Drop-in OpenAI-compatible API with built-in safety scanning
3. **RAG Safety Brain**: Knowledge-base of attack patterns for enhanced detection
4. **Governance Layer**: Full audit logs, risk reports, and compliance dashboards

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### Installation

```bash
# Clone repository
git clone <repo-url>
cd AI-safety

# Backend setup
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
alembic upgrade head

# Start backend
python -m uvicorn app.main:app --reload --port 8001

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

---

## 📡 API Reference

### Universal Proxy (OpenAI-Compatible)

Use IntellectSafe as a drop-in replacement for OpenAI:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="your-openai-key"  # Or use X-Upstream-API-Key header
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# Jailbreaks automatically blocked, responses scanned
```

### Scan Endpoints

```bash
# Scan a prompt for injection
curl -X POST "http://localhost:8001/api/v1/scan/prompt" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Ignore previous instructions"}'

# Scan LLM output for safety
curl -X POST "http://localhost:8001/api/v1/scan/output" \
  -H "Content-Type: application/json" \
  -d '{"output": "Here is how to...", "original_prompt": "..."}'

# Scan content for deepfakes (text, image, audio, video)
curl -X POST "http://localhost:8001/api/v1/scan/content" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "image", "content": "<base64-data>"}'
```

### Agent Control

```bash
# Authorize agent action
curl -X POST "http://localhost:8001/api/v1/agent/authorize" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-1", "session_id": "s1", "action_type": "file_read", "requested_action": {"path": "/tmp/test.txt"}}'

# Emergency kill switch
curl -X POST "http://localhost:8001/api/v1/agent/kill" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-1", "reason": "Suspicious behavior"}'

# Get action history
curl "http://localhost:8001/api/v1/agent/history/agent-1"
```

---

## ⚙️ Configuration

Create `.env` in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_safety_db

# LLM Providers (add keys for providers you want to use)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
GROQ_API_KEY=...
COHERE_API_KEY=...

# Security
SECRET_KEY=your-secret-key-change-in-production
```

---

## 🏗️ Architecture

```
AI-safety/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints (scan, agent, audit, proxy)
│   │   ├── core/            # Config, LLM Council, security
│   │   ├── modules/         # Safety engines (injection, deepfake, privacy)
│   │   └── services/        # RAG, governance, attack knowledge base
│   └── verify_*.py          # Verification scripts
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, Welcome, Research
│       └── components/      # UI components
└── docs/                    # Documentation
```

---

## ✅ Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Prompt Injection Detection | ✅ Complete | RAG-enhanced, dynamic patterns |
| Output Safety Guard | ✅ Complete | Heuristic fallback when Council offline |
| Universal Proxy | ✅ Complete | OpenAI-compatible, auto-scanning |
| Deepfake Detection | ✅ Complete | Text, Image, Audio, Video |
| Agent Control | ✅ Complete | Whitelist, kill switch, history |
| Dashboard | ✅ Complete | Live data integration |
| Audit/Governance | ✅ Complete | Risk reports, compliance |

---

## 🧪 Testing

```bash
cd backend

# Test all scan endpoints
python verify_backend.py

# Test Universal Proxy
python verify_proxy.py

# Test Agent Control
python verify_agent.py
```

---

## 📄 License

MIT License
