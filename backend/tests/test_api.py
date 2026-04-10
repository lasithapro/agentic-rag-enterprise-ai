"""Tests for API endpoints."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentType,
    ProcessingStatus,
    QueryResponse,
    ReportResponse,
    ActionType,
    HealthResponse,
)


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator."""
    orchestrator = MagicMock()
    orchestrator.ingest_file = AsyncMock(return_value=DocumentUploadResponse(
        document_id="test-doc-id",
        filename="test.pdf",
        document_type=DocumentType.PDF,
        status=ProcessingStatus.COMPLETED,
        message="Successfully ingested",
        chunks_created=10,
    ))
    orchestrator.ingest_web_url = AsyncMock(return_value=MagicMock(
        document_id="web-doc-id",
        url="https://example.com",
        status=ProcessingStatus.COMPLETED,
        message="Successfully ingested",
        chunks_created=5,
    ))
    orchestrator.query = AsyncMock(return_value=QueryResponse(
        query="Test query",
        answer="Test answer",
        sources=[],
        confidence_score=0.85,
        reasoning_steps=["Retrieved docs", "Generated response"],
        processing_time_ms=150.0,
    ))
    orchestrator.list_documents.return_value = [
        {"document_id": "doc-1", "filename": "test.pdf", "chunk_count": 10}
    ]
    orchestrator.vector_store = MagicMock()
    orchestrator.vector_store.delete_document.return_value = True
    orchestrator.vector_store.document_count = 1
    orchestrator.execute_action = AsyncMock(return_value=ReportResponse(
        report_id="report-1",
        action_type=ActionType.SUMMARIZE,
        title="Test Report",
        summary="Test summary",
        content="Test content",
        document_ids=["doc-1"],
    ))
    orchestrator.get_memory = MagicMock(return_value=MagicMock(
        __len__=MagicMock(return_value=2),
        get_history=MagicMock(return_value=[]),
    ))
    return orchestrator


@pytest.fixture
def client(mock_orchestrator):
    """Create a test client with mocked dependencies."""
    with patch("app.agents.orchestrator.AgentOrchestrator.get_instance", return_value=mock_orchestrator), \
         patch("app.api.routes.documents.get_orchestrator", return_value=lambda: mock_orchestrator), \
         patch("app.api.routes.query.get_orchestrator", return_value=lambda: mock_orchestrator), \
         patch("app.api.routes.reports.get_orchestrator", return_value=lambda: mock_orchestrator), \
         patch("app.api.routes.health.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            APP_VERSION="1.0.0",
            ENVIRONMENT="test",
            GOOGLE_API_KEY="test-key",
        )
        from app.main import app
        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_list_documents(client, mock_orchestrator):
    with patch("app.api.routes.documents.get_orchestrator", return_value=mock_orchestrator):
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
