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
2. **Universal Proxy**: Multi-provider API with built-in safety scanning (OpenAI-compatible interface)
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

### Universal Proxy (Multi-Provider Support)

IntellectSafe acts as a universal safety layer. Connect any major AI client and calls are automatically scanned:

| Provider | Model ID Example |
|----------|------------------|
| **OpenAI** | `gpt-4o`, `o1-mini` |
| **Groq** | `llama-3.3-70b-versatile` |
| **Anthropic** | `claude-3-5-sonnet-20241022` |
| **Google** | `gemini-2.5-flash`, `gemini-1.5-pro` |
| **Perplexity** | `sonar`, `sonar-pro` |

#### Integration Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",  # Point to IntellectSafe
    api_key="your-openai-key"             # Or use X-Upstream-API-Key header
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_headers={
        "X-Upstream-Provider": "openai"   # Optional: explicitly set provider
    }
)
```
*For detailed connection guides (LangChain, SDKs), see [docs/INTEGRATION.md](file:///c:/Users/USER/Desktop/cursor%20file/AI-safety/docs/INTEGRATION.md).*

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

# Scan content for deepfakes (Dual-Model Analysis)
# Detects Art (Midjourney/DALL-E) and Photorealistic Faces
curl -X POST "http://localhost:8001/api/v1/scan/content" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "image", "content": "<base64-data>"}'
```

### Agent Control (Level 5)

Full lifecycle protection for autonomous agents:
- **Authorization**: Permission gates for dangerous tools.
- **Kill Switch**: Immediate agent termination and block.
- **Audit**: Complete action history and session tracking.

```bash
# Authorize agent action
curl -X POST "http://localhost:8001/api/v1/agent/authorize" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent-1", "session_id": "s1", "action_type": "file_read", "requested_action": {"path": "/tmp/test.txt"}}'
```

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

**GPLv2**
GNU GENERAL PUBLIC LICENSE
Version 2 License
