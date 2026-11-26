from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.rag_service import is_gemini_configured

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        app="QueryNest",
        ai_mode="gemini" if is_gemini_configured() else "extractive-fallback",
    )
