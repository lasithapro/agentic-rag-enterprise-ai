"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_settings(monkeypatch):
    """Override settings for tests."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("VECTOR_STORE_PATH", "/tmp/test_vector_store")
    monkeypatch.setenv("UPLOAD_DIR", "/tmp/test_uploads")


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    service = MagicMock()
    service.generate = AsyncMock(return_value="Mock LLM response for testing")
    service.generate_with_context = AsyncMock(return_value={
        "answer": "Mock contextual response",
        "confidence": 0.85,
    })
    return service


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = MagicMock()
    store.similarity_search.return_value = []
    store.add_documents.return_value = 5
    store.list_documents.return_value = []
    store.document_count = 0
    return store


@pytest.fixture
def app_client():
    """Create a test client for the FastAPI app."""
    with patch("app.services.vector_store.VectorStoreService.__init__", return_value=None), \
         patch("app.services.llm_service.LLMService.__init__", return_value=None), \
         patch("app.services.vector_store.VectorStoreService._load_or_create_store"), \
         patch("app.services.vector_store.VectorStoreService._load_metadata"):
        from app.main import app
        with TestClient(app) as client:
            yield client
