"""Query and retrieval API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from app.agents.orchestrator import AgentOrchestrator
from app.models.schemas import QueryRequest, QueryResponse, MemoryResponse
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator.get_instance()


@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(
    request: QueryRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Query the knowledge base using the RAG pipeline."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return await orchestrator.query(request)


@router.get("/memory/{session_id}", response_model=MemoryResponse, tags=["Memory"])
async def get_session_memory(
    session_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Get conversation history for a session."""
    memory = orchestrator.get_memory(session_id)
    return MemoryResponse(
        session_id=session_id,
        message_count=len(memory),
        history=memory.get_history(),
    )


@router.delete("/memory/{session_id}", tags=["Memory"])
async def clear_session_memory(
    session_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Clear conversation history for a session."""
    orchestrator.clear_memory(session_id)
    return {"message": f"Memory cleared for session {session_id}"}
