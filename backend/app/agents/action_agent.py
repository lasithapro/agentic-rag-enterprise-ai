"""Action Agent - triggers specific actions like summarization and report generation."""
import time
from typing import List, Optional
from app.services.report_service import ReportService
from app.services.vector_store import VectorStoreService
from app.models.schemas import ReportResponse, ActionType, ComplianceCheckRequest
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ActionAgent:
    """
    Action Agent responsible for:
    - Document summarization
    - Compliance validation
    - Report generation
    - Entity extraction
    - Workflow automation
    """

    def __init__(self, report_service: ReportService, vector_store: VectorStoreService):
        self.report_service = report_service
        self.vector_store = vector_store
        logger.info("ActionAgent initialized")

    async def _get_document_contents(self, document_ids: List[str]) -> List[str]:
        """Retrieve document contents for specified document IDs."""
        contents = []
        for doc_id in document_ids:
            results = self.vector_store.similarity_search(
                query="document content overview",
                k=10,
                document_ids=[doc_id],
            )
            if results:
                doc_text = "\n".join([doc.page_content for doc, _ in results])
                contents.append(doc_text)
        return contents

    async def summarize(
        self,
        document_ids: List[str],
        query: Optional[str] = None,
    ) -> ReportResponse:
        """Generate a summary for specified documents."""
        logger.info("ActionAgent: summarize", document_ids=document_ids)
        contents = await self._get_document_contents(document_ids)
        if not contents:
            from app.models.schemas import ProcessingStatus
            import uuid
            return ReportResponse(
                report_id=str(uuid.uuid4()),
                action_type=ActionType.SUMMARIZE,
                title="Summary Report",
                summary="No document content found for the specified document IDs.",
                content="",
                document_ids=document_ids,
            )
        return await self.report_service.generate_summary(contents, document_ids, query)

    async def validate_compliance(
        self,
        document_ids: List[str],
        policy_document_ids: Optional[List[str]] = None,
        compliance_areas: Optional[List[str]] = None,
    ) -> ReportResponse:
        """Validate documents against compliance requirements."""
        logger.info("ActionAgent: validate_compliance", document_ids=document_ids)
        doc_contents = await self._get_document_contents(document_ids)
        policy_contents = None
        if policy_document_ids:
            policy_contents = await self._get_document_contents(policy_document_ids)

        return await self.report_service.generate_compliance_report(
            document_contents=doc_contents,
            document_ids=document_ids,
            policy_contents=policy_contents,
            compliance_areas=compliance_areas,
        )

    async def generate_report(
        self,
        document_ids: List[str],
        query: Optional[str] = None,
    ) -> ReportResponse:
        """Generate a comprehensive analysis report."""
        logger.info("ActionAgent: generate_report", document_ids=document_ids)
        contents = await self._get_document_contents(document_ids)
        if not contents:
            import uuid
            return ReportResponse(
                report_id=str(uuid.uuid4()),
                action_type=ActionType.GENERATE_REPORT,
                title="Analysis Report",
                summary="No document content found for the specified document IDs.",
                content="",
                document_ids=document_ids,
            )
        return await self.report_service.generate_full_report(contents, document_ids, query)
