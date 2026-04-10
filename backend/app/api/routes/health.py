"""Health check endpoints."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import get_settings
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    services = {
        "api": "healthy",
        "vector_store": "healthy",
        "llm": "configured" if settings.GOOGLE_API_KEY else "not_configured",
    }
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services,
    )


@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with service status."""
    from app.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator.get_instance()
    doc_count = orchestrator.vector_store.document_count
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "healthy",
            "vector_store": "healthy",
            "llm": "configured" if settings.GOOGLE_API_KEY else "not_configured",
        },
        "stats": {
            "indexed_documents": doc_count,
        },
    }
