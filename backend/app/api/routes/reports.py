"""Report generation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from app.agents.orchestrator import AgentOrchestrator
from app.models.schemas import (
    ReportRequest,
    ReportResponse,
    ComplianceCheckRequest,
    ActionType,
)
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator.get_instance()


@router.post("/reports/generate", response_model=ReportResponse, tags=["Reports"])
async def generate_report(
    request: ReportRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Generate a report for specified documents."""
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document ID is required")

    return await orchestrator.execute_action(
        action_type=request.action_type,
        document_ids=request.document_ids,
        query=request.query,
    )


@router.post("/reports/compliance", response_model=ReportResponse, tags=["Reports"])
async def check_compliance(
    request: ComplianceCheckRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Perform compliance validation on documents."""
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document ID is required")

    return await orchestrator.execute_action(
        action_type=ActionType.COMPLIANCE_CHECK,
        document_ids=request.document_ids,
        policy_document_ids=request.policy_document_ids,
        compliance_areas=request.compliance_areas,
    )


@router.post("/reports/summarize", response_model=ReportResponse, tags=["Reports"])
async def summarize_documents(
    request: ReportRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Generate a summary for specified documents."""
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document ID is required")

    return await orchestrator.execute_action(
        action_type=ActionType.SUMMARIZE,
        document_ids=request.document_ids,
        query=request.query,
    )
