"""Pydantic schemas for API request/response validation."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import time


class DocumentType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    TEXT = "text"
    WEB = "web"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    INGESTION = "ingestion"
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"
    ACTION = "action"


class ActionType(str, Enum):
    SUMMARIZE = "summarize"
    VALIDATE = "validate"
    GENERATE_REPORT = "generate_report"
    EXTRACT_ENTITIES = "extract_entities"
    COMPLIANCE_CHECK = "compliance_check"


# Document Schemas
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: DocumentType
    status: ProcessingStatus
    message: str
    chunks_created: int = 0


class WebIngestionRequest(BaseModel):
    url: str = Field(..., description="URL to ingest content from")
    session_id: Optional[str] = None


class WebIngestionResponse(BaseModel):
    document_id: str
    url: str
    status: ProcessingStatus
    message: str
    chunks_created: int = 0


# Query Schemas
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query")
    session_id: Optional[str] = Field(default=None, description="Session ID for memory")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    document_ids: Optional[List[str]] = Field(default=None, description="Filter by document IDs")
    include_sources: bool = Field(default=True, description="Include source documents in response")


class SourceDocument(BaseModel):
    document_id: str
    filename: str
    content: str
    score: float
    page_number: Optional[int] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceDocument] = []
    session_id: Optional[str] = None
    confidence_score: float = 0.0
    reasoning_steps: List[str] = []
    processing_time_ms: float = 0.0


# Report Schemas
class ReportRequest(BaseModel):
    document_ids: List[str] = Field(..., description="Document IDs to include in report")
    action_type: ActionType = Field(default=ActionType.GENERATE_REPORT)
    query: Optional[str] = Field(default=None, description="Specific query or focus for report")
    session_id: Optional[str] = None


class ComplianceCheckRequest(BaseModel):
    document_ids: List[str] = Field(..., description="Documents to check compliance for")
    policy_document_ids: Optional[List[str]] = Field(default=None, description="Policy documents to check against")
    compliance_areas: Optional[List[str]] = Field(default=None, description="Specific compliance areas to check")
    session_id: Optional[str] = None


class ComplianceIssue(BaseModel):
    area: str
    severity: str
    description: str
    recommendation: str


class ReportResponse(BaseModel):
    report_id: str
    action_type: ActionType
    title: str
    summary: str
    content: str
    key_findings: List[str] = []
    recommendations: List[str] = []
    compliance_issues: List[ComplianceIssue] = []
    document_ids: List[str] = []
    generated_at: float = Field(default_factory=time.time)
    processing_time_ms: float = 0.0


# Health Schemas
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: Dict[str, str] = {}


# Memory Schemas
class MemoryResponse(BaseModel):
    session_id: str
    message_count: int
    history: List[Dict[str, Any]] = []


# Agent Status
class AgentStatus(BaseModel):
    agent_type: AgentType
    status: str
    last_run: Optional[float] = None
    metadata: Dict[str, Any] = {}
