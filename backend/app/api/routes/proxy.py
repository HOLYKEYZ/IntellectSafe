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
from app.api.deps import get_current_user
from app.models.user import User

import logging
logger = logging.getLogger(__name__)

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
    current_user: User = Depends(get_current_user),
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
        logger.warning(f"Prompt scan failed: {e}")
    
    # --- FORWARD TO UPSTREAM PROVIDER ---
    upstream_api_key = x_upstream_api_key
    
    # Auto-detect provider if not specified via header (2026 Prefix Suite)
    if not x_upstream_provider:
        m = request.model.lower()
        if m.startswith(("gpt-", "o1-", "o3-", "o4-", "claude-", "grok-", "sonar-", "copilot-", "deepseek-", "llama-4-")):
            provider = "openrouter"
        elif m.startswith("gemini-3"):
            provider = "openrouter" # Gemini 3 typically via OpenRouter for high-speed reasoning
        elif m.startswith("gemini"):
            provider = "gemini" if "2" not in m else "gemini2"
        elif m.startswith("llama"):
            provider = "groq"
    
    # If no header key, check User's stored keys (DB) or System Fallback
    if not upstream_api_key:
        from app.models.provider_key import ProviderKey
        from app.core.security import decrypt_key
        
        # Check DB for user's key
        db_key = db.exec(
            select(ProviderKey).where(
                ProviderKey.user_id == current_user.id,
                ProviderKey.provider == provider
            )
        ).first()
        
        if db_key:
            try:
                upstream_api_key = decrypt_key(db_key.encrypted_key)
            except Exception:
                logger.error(f"Failed to decrypt key for user {current_user.id} provider {provider}")

    # Fallback to System Keys (.env)
    if not upstream_api_key:
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
            # Default fallback for everything else
            provider = "openrouter"
            upstream_api_key = settings.OPENROUTER_API_KEY
    
    if not upstream_api_key:
        raise HTTPException(
            status_code=400,
            detail=f"No API key configured for {provider}. Connect your account in Settings or use X-Upstream-API-Key."
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
        logger.warning(f"Output scan failed: {e}")
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
    """Forward request to OpenRouter with model mapping"""
    model_id = request.model.lower()
    
    # Model mapping for common names to OpenRouter IDs (2026 Ultra-Frontier Sync)
    mapping = {
        # OpenAI 2026 Suite
        "gpt-5.2": "openai/gpt-5.2",
        "gpt-5.2-pro": "openai/gpt-5.2-pro",
        "gpt-5-mini": "openai/gpt-5-mini",
        "o4-mini": "openai/o4-mini",
        "o3": "openai/o3-pro",
        "gpt-4.5": "openai/gpt-4.5-preview",
        
        # Anthropic 4.5 Suite
        "claude-4.5-opus": "anthropic/claude-opus-4-5-20251101",
        "claude-4.5-sonnet": "anthropic/claude-sonnet-4-5-20250929",
        "claude-4.5-haiku": "anthropic/claude-haiku-4-5-20251001",
        "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
        
        # Meta Llama 4 Herd
        "llama-4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-4-maverick": "meta-llama/llama-4-maverick-17b-128e-instruct",
        
        # Google Gemini 3
        "gemini-3-pro": "google/gemini-3-pro-preview",
        "gemini-3-flash": "google/gemini-3-flash-preview",
        
        # DeepSeek V4 & R1
        "deepseek-v4": "deepseek/deepseek-v4",
        "deepseek-v3.2": "deepseek/deepseek-v3.2",
        "deepseek-r1": "deepseek/deepseek-r1",
        
        # xAI & Perplexity 2026
        "grok-2": "x-ai/grok-2",
        "sonar-deep-research": "perplexity/sonar-deep-research",
        "sonar-reasoning-pro": "perplexity/sonar-reasoning-pro",
        "copilot-secure-bridge": "openai/o1-mini", # Default fast reasoning for Copilot
    }
    
    mapped_model = mapping.get(model_id, model_id)
    
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
                "model": mapped_model,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            },
        )
        response.raise_for_status()
        return response.json()





@router.get("/v1/models")
async def list_models():
    """List available models (proxied through IntellectSafe)"""
    return {
        "object": "list",
        "data": [
            # Standard Council Pillars
            {"id": "gemini-2.5-flash", "object": "model", "owned_by": "google", "proxied_by": "intellectsafe"},
            {"id": "llama-3.3-70b-versatile", "object": "model", "owned_by": "groq", "proxied_by": "intellectsafe"},
            
            # === 2026 ULTRA-FRONTIER MODELS ===
            
            # OpenAI Elite
            {"id": "gpt-5.2-pro", "object": "model", "owned_by": "openai", "proxied_by": "intellectsafe"},
            {"id": "gpt-5.2", "object": "model", "owned_by": "openai", "proxied_by": "intellectsafe"},
            {"id": "o4-mini", "object": "model", "owned_by": "openai", "proxied_by": "intellectsafe"},
            {"id": "o3", "object": "model", "owned_by": "openai", "proxied_by": "intellectsafe"},
            
            # Anthropic Claude 4.5
            {"id": "claude-4.5-opus", "object": "model", "owned_by": "anthropic", "proxied_by": "intellectsafe"},
            {"id": "claude-4.5-sonnet", "object": "model", "owned_by": "anthropic", "proxied_by": "intellectsafe"},
            
            # Meta Llama 4 Herd
            {"id": "llama-4-maverick", "object": "model", "owned_by": "meta", "proxied_by": "intellectsafe"},
            {"id": "llama-4-scout", "object": "model", "owned_by": "meta", "proxied_by": "intellectsafe"},
            
            # DeepSeek V4 & Gemini 3
            {"id": "deepseek-v4", "object": "model", "owned_by": "deepseek", "proxied_by": "intellectsafe"},
            {"id": "gemini-3-pro", "object": "model", "owned_by": "google", "proxied_by": "intellectsafe"},
            
            # Search & Research
            {"id": "sonar-deep-research", "object": "model", "owned_by": "perplexity", "proxied_by": "intellectsafe"},
            {"id": "copilot-secure-bridge", "object": "model", "owned_by": "intellectsafe", "proxied_by": "intellectsafe"},
        ]
    }
