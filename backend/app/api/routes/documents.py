"""Document ingestion API endpoints."""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.agents.orchestrator import AgentOrchestrator
from app.models.schemas import DocumentUploadResponse, WebIngestionRequest, WebIngestionResponse
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator.get_instance()


@router.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Upload and ingest a document (PDF, Word, or text)."""
    from pathlib import Path
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return await orchestrator.ingest_file(file)


@router.post("/documents/ingest-url", response_model=WebIngestionResponse, tags=["Documents"])
async def ingest_web_url(
    request: WebIngestionRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Ingest content from a web URL."""
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    return await orchestrator.ingest_web_url(request.url)


@router.get("/documents", tags=["Documents"])
async def list_documents(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """List all ingested documents."""
    documents = orchestrator.list_documents()
    return {"documents": documents, "total": len(documents)}


@router.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(
    document_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Delete a document from the knowledge base."""
    deleted = orchestrator.vector_store.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return {"message": f"Document {document_id} deleted successfully"}
