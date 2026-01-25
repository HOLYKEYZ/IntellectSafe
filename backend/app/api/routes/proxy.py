"""
Universal AI Safety Proxy

Multi-provider endpoints that intercept, scan, and forward requests.
Users just change their base_url to point to IntellectSafe.

Flow:
1. Receive request at /v1/chat/completions (OpenAI-compatible interface)
2. Scan prompt for injection (Level 1)
3. If safe, forward to upstream provider (OpenAI, Groq, Anthropic, Gemini, Perplexity)
4. Scan response for safety (Level 2)
5. Return response or block if unsafe
"""

import hashlib
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enhanced_council import EnhancedLLMCouncil
from app.models.database import ScanRequest
from app.services.db import get_db_session
from app.modules.enhanced_prompt_injection import EnhancedPromptInjectionDetector
from app.modules.output_safety import OutputSafetyGuard
from app.services.rag_system import RAGSystem

settings = get_settings()

router = APIRouter(tags=["proxy"])

# Initialize detectors
enhanced_council = EnhancedLLMCouncil()
rag_system = RAGSystem()
prompt_detector = EnhancedPromptInjectionDetector(enhanced_council, rag_system)
output_guard = OutputSafetyGuard(enhanced_council)


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    # Pass-through fields
    top_p: Optional[float] = None
    n: Optional[int] = None
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None


class ProxyConfig(BaseModel):
    """Configuration for upstream provider"""
    provider: str = "openai"  # "openai" or "anthropic"
    api_key: Optional[str] = None  # If not provided, use server's key


# Risk thresholds
BLOCK_THRESHOLD = 70.0
FLAG_THRESHOLD = 40.0


@router.post("/v1/chat/completions")
async def proxy_chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None),
    x_upstream_provider: Optional[str] = Header(None, alias="X-Upstream-Provider"),
    x_upstream_api_key: Optional[str] = Header(None, alias="X-Upstream-API-Key"),
    db: Session = Depends(get_db_session),
):
    """
    OpenAI-compatible chat completions endpoint with safety scanning.
    
    Headers:
    - Authorization: Bearer <your-api-key> (forwarded to upstream)
    - X-Upstream-Provider: "openai" or "anthropic" (default: openai)
    - X-Upstream-API-Key: Optional override for upstream API key
    
    Returns:
    - Standard OpenAI response if safe
    - 400 with block reason if unsafe prompt detected
    - 400 with block reason if unsafe response detected
    """
    provider = x_upstream_provider or "openai"
    
    # Extract the last user message for scanning
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")
    
    last_user_message = user_messages[-1].content
    
    # Create Scan Request
    input_hash = hashlib.sha256(last_user_message.encode()).hexdigest()
    scan_request = ScanRequest(
        id=uuid4(),
        request_type="proxy_chat",
        input_hash=input_hash,
        input_preview=last_user_message[:500],
        user_id=request.user,
        meta_data={"model": request.model, "provider": provider},
    )
    db.add(scan_request)
    db.commit()
    db.refresh(scan_request)
    
    # --- LEVEL 1: Scan Input Prompt ---
    try:
        prompt_risk = await prompt_detector.scan_fast(
            last_user_message,
            context={"model": request.model, "provider": provider},
        )
        
        # Save prompt risk score
        prompt_risk.scan_request_id = scan_request.id
        db.add(prompt_risk)
        db.commit()
        
        if prompt_risk.risk_score >= BLOCK_THRESHOLD:
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": f"Request blocked by IntellectSafe: {prompt_risk.explanation}",
                        "type": "safety_block",
                        "code": "prompt_injection_detected",
                        "risk_score": prompt_risk.risk_score,
                        "risk_level": prompt_risk.risk_level.value if hasattr(prompt_risk.risk_level, 'value') else str(prompt_risk.risk_level),
                    }
                }
            )
    except Exception as e:
        # Log but don't block on scan failure
        print(f"Warning: Prompt scan failed: {e}")
    
    # --- FORWARD TO UPSTREAM PROVIDER ---
    upstream_api_key = x_upstream_api_key
    if not upstream_api_key:
        # Fall back to server's configured key
        if provider == "gemini":
            upstream_api_key = settings.GEMINI_API_KEY
        elif provider == "groq":
            upstream_api_key = settings.GROQ_API_KEY
        elif provider == "gemini2":
            upstream_api_key = settings.GEMINI2_API_KEY
        elif provider == "grok2":
            upstream_api_key = settings.GROK2_API_KEY
        elif provider == "openrouter":
            upstream_api_key = settings.OPENROUTER_API_KEY
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    if not upstream_api_key:
        raise HTTPException(
            status_code=400,
            detail=f"No API key configured for {provider}. Provide X-Upstream-API-Key header or configure server."
        )
    
    try:
        if provider == "gemini":
            response_data = await _forward_to_gemini(request, upstream_api_key, settings.GEMINI_MODEL)
        elif provider == "groq":
            response_data = await _forward_to_groq(request, upstream_api_key, settings.GROQ_MODEL)
        elif provider == "gemini2":
            response_data = await _forward_to_gemini(request, upstream_api_key, settings.GEMINI2_MODEL)
        elif provider == "grok2":
            response_data = await _forward_to_groq(request, upstream_api_key, settings.GROK2_MODEL)
        elif provider == "openrouter":
            response_data = await _forward_to_openrouter(request, upstream_api_key)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"error": {"message": f"Upstream error: {e.response.text}", "type": "upstream_error"}}
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach upstream: {str(e)}")
    
    # --- LEVEL 2: Scan Output Response ---
    try:
        # Extract assistant response
        assistant_content = ""
        if "choices" in response_data and response_data["choices"]:
            assistant_content = response_data["choices"][0].get("message", {}).get("content", "")
        
        if assistant_content:
            output_risk = await output_guard.scan(
                assistant_content,
                original_prompt=last_user_message,
                context={"model": request.model, "provider": provider},
                scan_request_id=str(scan_request.id),
            )
            
            # Save output risk score
            output_risk.scan_request_id = scan_request.id
            db.add(output_risk)
            db.commit()
            
            if output_risk.risk_score >= BLOCK_THRESHOLD:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "message": f"Response blocked by IntellectSafe: {output_risk.explanation}",
                            "type": "safety_block",
                            "code": "unsafe_output_detected",
                            "risk_score": output_risk.risk_score,
                            "risk_level": output_risk.risk_level.value if hasattr(output_risk.risk_level, 'value') else str(output_risk.risk_level),
                        }
                    }
                )
            
            # Add safety metadata to response
            response_data["intellectsafe"] = {
                "prompt_scanned": True,
                "output_scanned": True,
                "output_risk_score": output_risk.risk_score,
                "output_risk_level": output_risk.risk_level.value if hasattr(output_risk.risk_level, 'value') else str(output_risk.risk_level),
            }
    except Exception as e:
        # Log but don't block on scan failure
        print(f"Warning: Output scan failed: {e}")
        response_data["intellectsafe"] = {
            "prompt_scanned": True,
            "output_scanned": False,
            "scan_error": str(e),
        }
    
    return response_data


async def _forward_to_groq(request: ChatCompletionRequest, api_key: str, model: str) -> Dict[str, Any]:
    """Forward request to Groq (OpenAI-compatible API)"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or 1024,
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()


async def _forward_to_gemini(request: ChatCompletionRequest, api_key: str, model: str) -> Dict[str, Any]:
    """Forward request to Google Gemini"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        contents = [{"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]} for m in request.messages]
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json={"contents": contents, "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_tokens or 1024}},
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return {"choices": [{"message": {"role": "assistant", "content": content}}], "model": model}


async def _forward_to_openrouter(request: ChatCompletionRequest, api_key: str) -> Dict[str, Any]:
    """Forward request to OpenRouter"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://intellectsafe.ai",
                "X-Title": "IntellectSafe Proxy",
            },
            json={
                "model": request.model or settings.OPENROUTER_MODEL,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
        )
        response.raise_for_status()
        return response.json()


async def _forward_to_groq(request: ChatCompletionRequest, api_key: str) -> Dict[str, Any]:
    """Forward request to Groq (OpenAI-compatible API)"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": request.model or "llama-3.3-70b-versatile",
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or 1024,
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()


async def _forward_to_gemini(request: ChatCompletionRequest, api_key: str) -> Dict[str, Any]:
    """Forward request to Google Gemini"""
    model = request.model or "gemini-2.5-flash"
    async with httpx.AsyncClient(timeout=60.0) as client:
        contents = [{"role": "user" if m.role == "user" else "model", "parts": [{"text": m.content}]} for m in request.messages]
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json={"contents": contents, "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_tokens or 1024}},
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return {"choices": [{"message": {"role": "assistant", "content": content}}], "model": model}




@router.get("/v1/models")
async def list_models():
    """List available models (proxied through IntellectSafe)"""
    return {
        "object": "list",
        "data": [
            {"id": "gemini-2.5-flash", "object": "model", "owned_by": "google", "proxied_by": "intellectsafe"},
            {"id": "llama-3.3-70b-versatile", "object": "model", "owned_by": "groq", "proxied_by": "intellectsafe"},
            {"id": "gpt-4o-mini", "object": "model", "owned_by": "openrouter", "proxied_by": "intellectsafe"},
        ]
    }
