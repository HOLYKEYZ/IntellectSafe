"""
Scan API endpoints

/scan/prompt - Scan prompts for injection
/scan/output - Scan outputs for safety
/scan/content - Scan content for deepfakes
"""

import hashlib
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.enhanced_council import EnhancedLLMCouncil
from app.models.database import ScanRequest
from app.modules.output_safety import OutputSafetyGuard
from app.modules.enhanced_prompt_injection import EnhancedPromptInjectionDetector
from app.modules.deepfake_detection import DeepfakeDetector
from app.services.rag_system import RAGSystem
from app.services.db import get_db_session
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scan", tags=["scan"])

# Initialize enhanced council, RAG, and detectors
enhanced_council = EnhancedLLMCouncil()
rag_system = RAGSystem()
prompt_detector = EnhancedPromptInjectionDetector(enhanced_council, rag_system)
output_guard = OutputSafetyGuard(enhanced_council)
deepfake_detector = DeepfakeDetector(enhanced_council)


class ScanPromptRequest(BaseModel):
    """Request model for prompt scanning"""
    prompt: str = Field(..., min_length=1, max_length=100000)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: Optional[list[str]] = None
    metadata: Optional[dict] = None


class ScanOutputRequest(BaseModel):
    """Request model for output scanning"""
    output: str = Field(..., min_length=1, max_length=100000)
    original_prompt: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict] = None


class ScanContentRequest(BaseModel):
    """Request model for content scanning"""
    content_type: str = Field(..., pattern="^(text|image|video|audio)$")
    content: Optional[str] = None
    content_url: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict] = None


class ScanResponse(BaseModel):
    """Response model for scan results"""
    scan_request_id: str
    verdict: str
    risk_score: float
    risk_level: str
    confidence: float
    explanation: str
    signals: dict
    false_positive_probability: Optional[float] = None
    timestamp: datetime


@router.post("/prompt", response_model=ScanResponse)
async def scan_prompt(
    request: ScanPromptRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Scan a prompt for injection and manipulation attempts

    Enhanced with RAG system and advanced detection.
    Returns structured JSON with risk assessment and explainability.
    """
    try:
        # Create scan request record
        input_hash = hashlib.sha256(request.prompt.encode()).hexdigest()
        scan_request = ScanRequest(
            id=uuid4(),
            request_type="prompt",
            input_hash=input_hash,
            input_preview=request.prompt[:500],
            user_id=request.user_id,
            session_id=request.session_id,
            meta_data={
                **(request.metadata or {}),
                "has_conversation_history": bool(request.conversation_history),
            },
        )
        db.add(scan_request)
        db.commit()
        db.refresh(scan_request)

        # Run FAST detection (heuristic only - no LLM calls for speed)
        # Use scan_enhanced() instead if you need full LLM Council analysis
        risk_score = await prompt_detector.scan_fast(
            request.prompt,
            context={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "conversation_history": request.conversation_history or [],
                **(request.metadata or {}),
            },
            scan_request_id=str(scan_request.id),
        )

        # Save risk score
        risk_score.scan_request_id = scan_request.id
        db.add(risk_score)
        db.commit()

        return ScanResponse(
            scan_request_id=str(scan_request.id),
            verdict=risk_score.verdict,
            risk_score=risk_score.risk_score,
            risk_level=risk_score.risk_level.value,
            confidence=risk_score.confidence,
            explanation=risk_score.explanation,
            signals=risk_score.signals,
            false_positive_probability=risk_score.false_positive_probability,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/output", response_model=ScanResponse)
async def scan_output(
    request: ScanOutputRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Scan an LLM output for safety issues

    Returns structured JSON with risk assessment.
    """
    try:
        # Create scan request record
        input_hash = hashlib.sha256(request.output.encode()).hexdigest()
        scan_request = ScanRequest(
            id=uuid4(),
            request_type="output",
            input_hash=input_hash,
            input_preview=request.output[:500],
            user_id=request.user_id,
            session_id=request.session_id,
            meta_data=request.metadata or {},
        )
        db.add(scan_request)
        db.commit()
        db.refresh(scan_request)

        # Run detection
        risk_score = await output_guard.scan(
            request.output,
            original_prompt=request.original_prompt,
            context={
                "user_id": request.user_id,
                "session_id": request.session_id,
                **(request.metadata or {}),
            },
            scan_request_id=str(scan_request.id),
        )

        # Save risk score
        risk_score.scan_request_id = scan_request.id
        db.add(risk_score)
        db.commit()

        return ScanResponse(
            scan_request_id=str(scan_request.id),
            verdict=risk_score.verdict,
            risk_score=risk_score.risk_score,
            risk_level=risk_score.risk_level.value,
            confidence=risk_score.confidence,
            explanation=risk_score.explanation,
            signals=risk_score.signals,
            false_positive_probability=risk_score.false_positive_probability,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/content", response_model=ScanResponse)
async def scan_content(
    request: ScanContentRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Scan content for deepfake detection (text, image, video, audio)

    Supports:
    - Text: AI-generated text detection
    - Image: Deepfake image detection (placeholder)
    - Video: Deepfake video detection (placeholder)
    - Audio: Deepfake voice detection (placeholder)
    """
    try:
        if request.content_type == "text":
            if not request.content:
                raise HTTPException(
                    status_code=400, detail="Content required for text scanning"
                )

            # Create scan request record
            input_hash = hashlib.sha256(request.content.encode()).hexdigest()
            scan_request = ScanRequest(
                id=uuid4(),
                request_type="content_text",
                input_hash=input_hash,
                input_preview=request.content[:500],
                user_id=request.user_id,
                session_id=request.session_id,
                meta_data={**(request.metadata or {}), "content_type": "text"},
            )
            db.add(scan_request)
            db.commit()
            db.refresh(scan_request)

            # Run deepfake detection
            risk_score = await deepfake_detector.scan_text(
                request.content,
                context={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    **(request.metadata or {}),
                },
                scan_request_id=str(scan_request.id),
            )

            # Save risk score
            risk_score.scan_request_id = scan_request.id
            db.add(risk_score)
            db.commit()

            return ScanResponse(
                scan_request_id=str(scan_request.id),
                verdict=risk_score.verdict,
                risk_score=risk_score.risk_score,
                risk_level=risk_score.risk_level.value,
                confidence=risk_score.confidence,
                explanation=risk_score.explanation,
                signals=risk_score.signals,
                false_positive_probability=risk_score.false_positive_probability,
                timestamp=datetime.utcnow(),
            )

        elif request.content_type == "image":
            if not request.content:
                 raise HTTPException(status_code=400, detail="Content required")
            
            # Create scan request
            input_hash = hashlib.sha256(request.content.encode()).hexdigest()
            scan_request = ScanRequest(
                id=uuid4(),
                request_type="content_image",
                input_hash=input_hash,
                input_preview=f"Image content ({len(request.content)} chars)",
                user_id=request.user_id,
                session_id=request.session_id,
                meta_data={**(request.metadata or {}), "content_type": "image"},
            )
            db.add(scan_request)
            db.commit()

            risk_score = await deepfake_detector.scan_image(
                request.content,
                context={"user_id": request.user_id, **(request.metadata or {})},
                scan_request_id=str(scan_request.id),
            )
            
            risk_score.scan_request_id = scan_request.id
            db.add(risk_score)
            db.commit()

            return ScanResponse(
                scan_request_id=str(scan_request.id),
                verdict=risk_score.verdict,
                risk_score=risk_score.risk_score,
                risk_level=risk_score.risk_level.value,
                confidence=risk_score.confidence,
                explanation=risk_score.explanation,
                signals=risk_score.signals,
                false_positive_probability=risk_score.false_positive_probability,
                timestamp=datetime.utcnow(),
            )

        elif request.content_type == "audio":
             if not request.content:
                 raise HTTPException(status_code=400, detail="Content required")
            
             input_hash = hashlib.sha256(request.content.encode()).hexdigest()
             scan_request = ScanRequest(
                id=uuid4(),
                request_type="content_audio",
                input_hash=input_hash,
                input_preview=f"Audio content ({len(request.content)} chars)",
                user_id=request.user_id,
                session_id=request.session_id,
                meta_data={**(request.metadata or {}), "content_type": "audio"},
            )
             db.add(scan_request)
             db.commit()

             risk_score = await deepfake_detector.scan_audio(
                request.content,
                context={"user_id": request.user_id, **(request.metadata or {})},
                scan_request_id=str(scan_request.id),
            )
            
             risk_score.scan_request_id = scan_request.id
             db.add(risk_score)
             db.commit()

             return ScanResponse(
                scan_request_id=str(scan_request.id),
                verdict=risk_score.verdict,
                risk_score=risk_score.risk_score,
                risk_level=risk_score.risk_level.value,
                confidence=risk_score.confidence,
                explanation=risk_score.explanation,
                signals=risk_score.signals,
                false_positive_probability=risk_score.false_positive_probability,
                timestamp=datetime.utcnow(),
            )

        elif request.content_type == "video":
             if not request.content:
                 raise HTTPException(status_code=400, detail="Content required")
            
             input_hash = hashlib.sha256(request.content.encode()).hexdigest()
             scan_request = ScanRequest(
                id=uuid4(),
                request_type="content_video",
                input_hash=input_hash,
                input_preview=f"Video content ({len(request.content)} chars)",
                user_id=request.user_id,
                session_id=request.session_id,
                meta_data={**(request.metadata or {}), "content_type": "video"},
            )
             db.add(scan_request)
             db.commit()

             risk_score = await deepfake_detector.scan_video(
                request.content,
                context={"user_id": request.user_id, **(request.metadata or {})},
                scan_request_id=str(scan_request.id),
            )
            
             risk_score.scan_request_id = scan_request.id
             db.add(risk_score)
             db.commit()

             return ScanResponse(
                scan_request_id=str(scan_request.id),
                verdict=risk_score.verdict,
                risk_score=risk_score.risk_score,
                risk_level=risk_score.risk_level.value,
                confidence=risk_score.confidence,
                explanation=risk_score.explanation,
                signals=risk_score.signals,
                false_positive_probability=risk_score.false_positive_probability,
                timestamp=datetime.utcnow(),
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported content type: {request.content_type}"
            )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Content scan failed: {str(e)}")
