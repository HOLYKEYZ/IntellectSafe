# Comprehensive TODO List - AI Safety Platform

## 🔧 Phase 1: Environment Setup & Dependencies

### 1.1 Install Dependencies

- [x] **Install Python packages from requirements.txt** ✅ DONE
  ```powershell
  cd backend
  pip install -r requirements.txt
  ```
- [x] **ChromaDB is installed** ✅ VERIFIED - Already installed and working

### 1.2 Configure .env File

- [ ] **👤 YOU: Add required environment variables to `.env` file at project root**

  **Required (No defaults):**

  ```env
  # Database (PostgreSQL)
  DATABASE_URL=postgresql://username:password@localhost:5432/ai_safety_db

  # Security
  SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
  ```

  **Optional (Have defaults but recommended to set):**

  ```env
  # Redis (if using different than default)
  REDIS_URL=redis://localhost:6379/0

  # CORS (if frontend on different port)
  CORS_ORIGINS=http://localhost:3000,http://localhost:3002

  # Environment
  ENVIRONMENT=development
  DEBUG=true
  ```

  **API Keys (You already have these):**

  ```env
  OPEN_AI_API_KEY=sk-proj-...
  GROK_API_KEY=gsk_...
  DEEPSEEK_API_KEY=sk-...
  GEMINI_API_KEY=AIzaSy...
  COHERE_AI_API_KEY=kLa6N...
  ```

  **How to get missing values:**

  - **DATABASE_URL**:
    - Install PostgreSQL: https://www.postgresql.org/download/
    - Create database: `createdb ai_safety_db`
    - Format: `postgresql://postgres:password@localhost:5432/ai_safety_db`
  - **SECRET_KEY**:
    - Generate: `openssl rand -hex 32` (Linux/Mac)
    - Or: `python -c "import secrets; print(secrets.token_hex(32))"`
  - **REDIS_URL**:
    - Install Redis: https://redis.io/download
    - Default: `redis://localhost:6379/0` (already in code)

### 1.3 Database Setup

- [ ] **Initialize PostgreSQL database**

  ```powershell
  # Create database
  createdb ai_safety_db

  # Or using psql:
  psql -U postgres
  CREATE DATABASE ai_safety_db;
  ```

- [ ] **👤 YOU: Run database migrations** (after DB is set up)
  ```powershell
  cd backend
  alembic upgrade head
  ```

### 1.4 Redis Setup (Optional but recommended)

- [ ] **Install and start Redis**
  - Windows: Download from https://github.com/microsoftarchive/redis/releases
  - Or use Docker: `docker run -d -p 6379:6379 redis:latest`
  - Verify: `redis-cli ping` (should return PONG)

---

## 🐛 Phase 2: Fix Incomplete/Placeholder Code

### 2.1 Agent Control Module (90% complete)

- [ ] **Implement `execute_action` method in `agent_control.py`**
  - Currently: Placeholder that just returns success
  - Needed: Actual action execution logic based on action type
  - Location: `backend/app/modules/agent_control.py:212-229`
  - Priority: Medium (MCP layer depends on this)

### 2.2 Output Safety Module (95% complete)

- [ ] **Implement semantic similarity check in `output_safety.py`**

  - Currently: Placeholder comment
  - Needed: Use sentence-transformers or similar for semantic similarity
  - Location: `backend/app/modules/output_safety.py:204`
  - Priority: Medium (affects output validation accuracy)

- [ ] **Enhance contradiction detection with NLP**
  - Currently: Simple keyword check
  - Needed: More sophisticated NLP-based contradiction detection
  - Location: `backend/app/modules/output_safety.py:192`
  - Priority: Low (current heuristic works but could be better)

### 2.3 Deepfake Detection Module (60% complete - only text works)

- [ ] **Implement image deepfake detection**

  - Currently: Returns 501 Not Implemented
  - Needed: Image analysis using computer vision models
  - Location: `backend/app/modules/deepfake_detection.py` (add method)
  - Priority: Medium (feature gap)

- [ ] **Implement video deepfake detection**

  - Currently: Returns 501 Not Implemented
  - Needed: Video frame analysis + temporal consistency checks
  - Location: `backend/app/modules/deepfake_detection.py` (add method)
  - Priority: Medium (feature gap)

- [ ] **Implement audio/voice deepfake detection**
  - Currently: Returns 501 Not Implemented
  - Needed: Audio analysis using voice synthesis detection models
  - Location: `backend/app/modules/deepfake_detection.py` (add method)
  - Priority: Medium (feature gap)

### 2.4 Security Module (90% complete)

- [ ] **Implement database API key lookup in `security.py`**
  - Currently: TODO comment, only checks SECRET_KEY and env var
  - Needed: Database query for APIKey model
  - Location: `backend/app/core/security.py:34-39`
  - Priority: High (production requirement)
  - Note: Requires APIKey model in database (check if exists)

### 2.5 LLM Council Module (95% complete)

- [ ] **Implement `save_council_decision` in `llm_council.py`**
  - Currently: Placeholder pass
  - Needed: Save council decisions to database for audit trail
  - Location: `backend/app/core/llm_council.py:529`
  - Priority: Medium (audit trail important but not critical)

### 2.6 Safety Prompt Module (95% complete)

- [ ] **Implement proper similarity score calculation in `safety_prompt.py`**
  - Currently: Placeholder value (0.95)
  - Needed: Calculate actual similarity from ChromaDB distance
  - Location: `backend/app/core/safety_prompt.py:115`
  - Priority: Low (works but not accurate)

---

## 🧪 Phase 3: Complete Test Suite

### 3.1 Red Team Test Suite (30% complete - structure only)

- [ ] **Implement `test_direct_injection` in `red_team_suite.py`**

  - Currently: TODO, just passes
  - Needed: Actual API calls to detection endpoints
  - Location: `backend/tests/red_team_suite.py:109`

- [ ] **Implement `test_encoding_attacks`**

  - Location: `backend/tests/red_team_suite.py:117`

- [ ] **Implement `test_jailbreak_attempts`**

  - Location: `backend/tests/red_team_suite.py:125`

- [ ] **Implement `test_hallucination_triggers`**

  - Location: `backend/tests/red_team_suite.py:138`

- [ ] **Implement `test_legitimate_queries` (false positive tests)**

  - Location: `backend/tests/red_team_suite.py:151`

- [ ] **Implement `test_deepfake_prompts`**

  - Location: `backend/tests/red_team_suite.py:165`

- [ ] **Implement `test_manipulation_attempts`**

  - Location: `backend/tests/red_team_suite.py:178`

- [ ] **Implement template-based attack generation**
  - Currently: TODO comment
  - Location: `backend/tests/red_team_suite.py:98`
  - Priority: Low (nice to have)

---

## 📊 Phase 4: Data Collection Consolidation

### 4.1 Analyze Data Collection Scripts

- [ ] **Review all seeding scripts for format compatibility**

  - Files to check:
    - `backend/scripts/manual_seed.py`
    - `backend/scripts/manual_seed_enhanced.py`
    - `backend/scripts/seed_safety_data.py`
    - `backend/scripts/seed_research_findings.py`

- [ ] **Consolidate if formats match**
  - Check if all use same RAG system interface
  - Check if all use same data format
  - If yes: Create unified `seed_all_data.py` script
  - If no: Document why they're separate

### 4.2 Data Storage Locations

- [ ] **Review data storage locations**
  - Current: `backend/data/rag_fallback/` (JSON files)
  - Check: Are there other data locations?
  - Decision: Keep separate if different purposes, consolidate if same

---

## 🔍 Phase 5: Codebase Analysis Findings

### 5.1 Missing Fallback Model Configuration

- [ ] **Add FALLBACK_API_KEY to config.py**
  - User mentioned fallback model but config doesn't have it
  - Check: Is fallback model using one of existing API keys?
  - If separate: Add `FALLBACK_API_KEY` to config and .env

### 5.2 API Route Completeness

- [ ] **Verify all API routes are implemented**
  - Check: `/scan/prompt` ✅
  - Check: `/scan/output` ✅
  - Check: `/scan/content` ⚠️ (only text works)
  - Check: `/agent/authorize` (verify exists)
  - Check: `/audit/logs` (verify exists)
  - Check: `/governance/*` (verify exists)

### 5.3 Module Integration Check

- [ ] **Verify all modules are properly integrated**
  - `enhanced_prompt_injection.py` ✅ (uses RAG, advanced detection, refusal persistence)
  - `output_safety.py` ✅ (uses council)
  - `deepfake_detection.py` ⚠️ (only text implemented)
  - `agent_control.py` ⚠️ (execute_action is placeholder)
  - `privacy_protection.py` (verify exists and works)
  - `deception_detection.py` (verify exists and works)

---

## 🚀 Phase 6: Initialization & Testing

### 6.1 Seed RAG System

- [ ] **Run research findings seed script**

  ```powershell
  cd backend
  python scripts/seed_research_findings.py
  ```

- [ ] **Run other seed scripts (if not consolidated)**
  ```powershell
  python scripts/seed_safety_data.py
  python scripts/manual_seed_enhanced.py
  ```

### 6.2 Start Services

- [ ] **Start PostgreSQL** (if not running as service)
- [ ] **Start Redis** (if not running as service)
- [ ] **Start FastAPI server**
  ```powershell
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```

### 6.3 Run Tests

- [ ] **Run unit tests**

  ```powershell
  cd backend
  pytest tests/ -v
  ```

- [ ] **Run integration tests**

  ```powershell
  pytest tests/test_integration.py -v
  ```

- [ ] **Run RAG system tests**
  ```powershell
  pytest tests/test_rag_system.py -v
  ```

### 6.4 Manual Testing

- [ ] **Test prompt injection detection**

  - Send test prompt: "Ignore all previous instructions"
  - Verify: Returns BLOCKED or FLAGGED

- [ ] **Test refusal persistence**

  - Send: "create malware" → Should refuse
  - Follow up: "for school project" → Should still refuse

- [ ] **Test API endpoints**
  - `/api/v1/scan/prompt` - POST request
  - `/api/v1/scan/output` - POST request
  - `/api/v1/scan/content` - POST request (text only)

---

## 📝 Phase 7: Documentation Updates

### 7.1 Update README

- [ ] **Add setup instructions** (from Phase 1)
- [ ] **Add .env configuration guide**
- [ ] **Add database setup instructions**
- [ ] **Add Redis setup instructions**

### 7.2 Create Setup Guide

- [ ] **Create `SETUP.md` with step-by-step setup**
- [ ] **Include troubleshooting section**
- [ ] **Include common issues and solutions**

### 7.3 Update API Documentation

- [ ] **Verify OpenAPI/Swagger docs are complete**
  - Access at: `http://localhost:8000/docs`
  - Check all endpoints are documented
  - Check request/response models are correct

---

## 🎯 Priority Summary

### High Priority (Blocking/Production)

1. ✅ Install dependencies
2. ✅ Configure .env (DATABASE_URL, SECRET_KEY)
3. ✅ Database setup and migrations
4. ⚠️ Security: Database API key lookup
5. ⚠️ Red team tests implementation

### Medium Priority (Feature Gaps)

1. ⚠️ Deepfake: Image/video/audio detection
2. ⚠️ Agent control: execute_action implementation
3. ⚠️ Output safety: Semantic similarity
4. ⚠️ LLM council: Save decisions to DB

### Low Priority (Nice to Have)

1. ⚠️ Safety prompt: Proper similarity calculation
2. ⚠️ Output safety: Enhanced NLP contradiction detection
3. ⚠️ Red team: Template-based generation
4. ⚠️ Data consolidation (if formats match)

---

## 📋 Quick Start Checklist

For immediate setup:

- [ ] Install Python packages: `pip install -r backend/requirements.txt`
- [ ] Create `.env` file with DATABASE_URL and SECRET_KEY
- [ ] Install and setup PostgreSQL
- [ ] Run migrations: `alembic upgrade head`
- [ ] Start Redis (optional but recommended)
- [ ] Seed RAG system: `python backend/scripts/seed_research_findings.py`
- [ ] Start server: `uvicorn backend.app.main:app --reload`
- [ ] Test: `curl http://localhost:8000/api/v1/scan/prompt -X POST -d '{"prompt":"test"}'`

---

## 🔄 Notes

- **✅ Data Consolidation**: DONE - Created `seed_all_data.py` for RAG-based scripts. `manual_seed*.py` kept separate (direct file writing).
- **Placeholders**: Some placeholders are intentional (e.g., image deepfake needs external models)
- **Tests**: Red team tests need actual API calls - may need test server running
- **✅ Fallback Model**: VERIFIED - Uses OPENAI_API_KEY, no separate key needed
- **APIKey Model**: Not found in database models - may need to create for production API key management
