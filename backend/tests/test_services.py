"""Tests for service components."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.document_processor import DocumentProcessor
from app.services.report_service import ReportService
from app.models.schemas import ActionType


class TestDocumentProcessor:
    def test_initialization(self, tmp_path):
        with patch("app.services.document_processor.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                UPLOAD_DIR=str(tmp_path / "uploads"),
                CHUNK_SIZE=1000,
                CHUNK_OVERLAP=200,
            )
            processor = DocumentProcessor()
            assert processor.upload_dir.exists()

    def test_process_text_file(self, tmp_path):
        with patch("app.services.document_processor.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                UPLOAD_DIR=str(tmp_path / "uploads"),
                CHUNK_SIZE=1000,
                CHUNK_OVERLAP=200,
            )
            processor = DocumentProcessor()
            test_file = tmp_path / "test.txt"
            test_file.write_text("This is test content for processing. " * 50)
            chunks = processor.process_text(test_file, "doc-123", "test.txt")
            assert len(chunks) > 0
            assert chunks[0].metadata["document_id"] == "doc-123"


@pytest.mark.asyncio
class TestReportService:
    async def test_generate_summary(self):
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="Summary: This document covers compliance topics.")
        service = ReportService(mock_llm)
        result = await service.generate_summary(
            document_contents=["Document content about regulations"],
            document_ids=["doc-1"],
        )
        assert result.action_type == ActionType.SUMMARIZE
        assert result.report_id is not None

    async def test_generate_compliance_report(self):
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="Compliance Status: The document has some issues.")
        service = ReportService(mock_llm)
        result = await service.generate_compliance_report(
            document_contents=["Policy document content"],
            document_ids=["doc-1"],
            compliance_areas=["GDPR", "SOX"],
        )
        assert result.action_type == ActionType.COMPLIANCE_CHECK
        assert result.report_id is not None
