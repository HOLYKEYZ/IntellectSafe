# AI Safety & Security Platform

Production-grade AI Safety Engine protecting humans, organizations, and AI systems from misuse, deception, manipulation, and loss of control.

## Architecture

### Core Components

1. **LLM Council** - Multi-model validation with weighted voting
2. **Safety Modules** - 7 independent detection engines
3. **MCP Layer** - Agent control and permission gates
4. **Audit Engine** - Immutable logging and compliance
5. **Web Dashboard** - Human analysis and verification

### Tech Stack

- **Backend**: FastAPI, PostgreSQL, Redis, Celery
- **Frontend**: React, TypeScript, shadcn/ui
- **Deployment**: Render
- **LLM Providers**: OpenAI, Claude, Gemini, DeepSeek, Groq, Cohere

## Project Structure

```
AI-safety/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, security, LLM council
│   │   ├── models/       # Database models
│   │   ├── modules/      # Safety modules
│   │   ├── services/     # Business logic
│   │   └── workers/      # Background tasks
│   ├── alembic/          # DB migrations
│   └── tests/            # Test suites
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Dashboard pages
│   │   └── lib/          # Utilities
│   └── public/
├── mcp/                  # MCP server implementation
└── docs/                 # Architecture docs

```

## Getting Started

Please refer to **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** for the complete documentation, including:
- Full Setup Guide (Backend & Frontend)
- Architecture Overview
- Implementation Status
- Research & Data Collection Guide

## Security Principles

- Zero trust architecture
- No single-model decisions
- All decisions logged and explainable
- Defense in depth
- Deterministic behavior where possible

