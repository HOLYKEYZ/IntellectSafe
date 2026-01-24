# IntellectSafe Integration Guide

Connect your AI applications to IntellectSafe for automatic safety scanning.

## Quick Start

Replace your AI provider's base URL with IntellectSafe:

```python
# Python (OpenAI SDK)
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001",  # Point to IntellectSafe
    api_key="your-openai-key"  # Or use X-Upstream-API-Key header
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Supported Providers

| Provider   | Header: X-Upstream-Provider | Models |
|------------|---------------------------|--------|
| OpenAI     | `openai`                  | gpt-4o, gpt-4-turbo, gpt-3.5-turbo |
| Groq       | `groq`                    | llama-3.1-70b-versatile |
| Google     | `gemini`                  | gemini-1.5-pro, gemini-1.5-flash |
| Anthropic  | `anthropic` or `claude`   | claude-sonnet-4-20250514, claude-3-opus |
| Perplexity | `perplexity`              | llama-3.1-sonar-large-128k-online |

## Headers

```
X-Upstream-Provider: groq          # Select provider
X-Upstream-API-Key: sk-xxx         # Provider API key (optional if server configured)
```

## LangChain Integration

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8001",
    model="gpt-4o",
    api_key="your-key"
)
```

## Agent SDK (Claude Code, Antigravity, etc.)

For agent frameworks, configure the base URL in your agent's config:

```yaml
# .agent/config.yaml
llm:
  base_url: http://localhost:8001
  provider: openai
  model: gpt-4o
```

All agent actions will be automatically scanned before execution.

## What Gets Scanned

1. **Prompts**: Checked for injection attacks, jailbreaks, social engineering
2. **Outputs**: Checked for harmful content, data leakage, policy violations
3. **Agent Actions**: Dangerous operations (file writes, network calls) require approval

## Response Format

Successful responses include safety metadata:

```json
{
  "choices": [...],
  "intellectsafe": {
    "prompt_scanned": true,
    "output_scanned": true,
    "output_risk_score": 15.2,
    "output_risk_level": "SAFE"
  }
}
```

Blocked responses return 400 with details:

```json
{
  "error": {
    "message": "Request blocked by IntellectSafe: Prompt injection detected",
    "type": "safety_block",
    "code": "prompt_injection_detected",
    "risk_score": 85.0
  }
}
```
