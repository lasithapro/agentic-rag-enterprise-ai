"""Agent Orchestrator - coordinates all agents in the pipeline."""
from typing import List, Optional
from fastapi import UploadFile
from app.agents.ingestion_agent import IngestionAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.agents.action_agent import ActionAgent
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.services.report_service import ReportService
from app.core.memory import MemoryManager
from app.models.schemas import (
    DocumentUploadResponse,
    WebIngestionResponse,
    QueryResponse,
    QueryRequest,
    ReportResponse,
    ActionType,
    ComplianceCheckRequest,
    SourceDocument,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent pipeline:
    IngestionAgent -> VectorStore -> RetrievalAgent -> ReasoningAgent -> ActionAgent
    
    Manages agent lifecycle and coordinates data flow between agents.
    """

    _instance: Optional["AgentOrchestrator"] = None

    def __init__(self):
        logger.info("Initializing AgentOrchestrator")
        # Initialize services
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.report_service = ReportService(self.llm_service)
        self.memory_manager = MemoryManager()

        # Initialize agents
        self.ingestion_agent = IngestionAgent(self.doc_processor, self.vector_store)
        self.retrieval_agent = RetrievalAgent(self.vector_store)
        self.reasoning_agent = ReasoningAgent(self.llm_service, self.memory_manager)
        self.action_agent = ActionAgent(self.report_service, self.vector_store)

        logger.info("AgentOrchestrator initialized successfully")

    @classmethod
    def get_instance(cls) -> "AgentOrchestrator":
        """Get singleton orchestrator instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # Ingestion Pipeline
    async def ingest_file(self, file: UploadFile) -> DocumentUploadResponse:
        """Ingest a document file through the ingestion agent."""
        logger.info("Orchestrator: ingest_file", filename=file.filename)
        return await self.ingestion_agent.ingest_file(file)

    async def ingest_web_url(self, url: str) -> WebIngestionResponse:
        """Ingest web content through the ingestion agent."""
        logger.info("Orchestrator: ingest_web_url", url=url)
        return await self.ingestion_agent.ingest_web_url(url)

    # RAG Query Pipeline
    async def query(self, request: QueryRequest) -> QueryResponse:
        """Execute the full RAG pipeline: Retrieve -> Reason -> Respond."""
        import time
        start_time = time.time()
        logger.info("Orchestrator: query", query=request.query[:50])

        # Step 1: Retrieve relevant documents
        source_docs = await self.retrieval_agent.retrieve(
            query=request.query,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )

        # Step 2: Reason with retrieved context
        reasoning_result = await self.reasoning_agent.reason(
            query=request.query,
            source_docs=source_docs,
            session_id=request.session_id,
        )

        # Step 3: Build response
        sources = source_docs if request.include_sources else []
        total_time = (time.time() - start_time) * 1000

        return QueryResponse(
            query=request.query,
            answer=reasoning_result["answer"],
            sources=sources,
            session_id=request.session_id,
            confidence_score=reasoning_result["confidence"],
            reasoning_steps=reasoning_result["reasoning_steps"],
            processing_time_ms=total_time,
        )

    # Action Pipeline
    async def execute_action(
        self,
        action_type: ActionType,
        document_ids: List[str],
        query: Optional[str] = None,
        policy_document_ids: Optional[List[str]] = None,
        compliance_areas: Optional[List[str]] = None,
    ) -> ReportResponse:
        """Execute a specific action through the action agent."""
        logger.info("Orchestrator: execute_action", action_type=action_type, document_ids=document_ids)

        if action_type == ActionType.SUMMARIZE:
            return await self.action_agent.summarize(document_ids, query)
        elif action_type == ActionType.COMPLIANCE_CHECK:
            return await self.action_agent.validate_compliance(
                document_ids, policy_document_ids, compliance_areas
            )
        elif action_type == ActionType.GENERATE_REPORT:
            return await self.action_agent.generate_report(document_ids, query)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    # Utility
    def list_documents(self):
        """List all ingested documents."""
        return self.vector_store.list_documents()

    def get_memory(self, session_id: str):
        """Get memory for a session."""
        return self.memory_manager.get_session_memory(session_id)

    def clear_memory(self, session_id: str) -> None:
        """Clear memory for a session."""
        self.memory_manager.delete_session(session_id)
