"""Tests for agent components."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.agents.ingestion_agent import IngestionAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.agents.action_agent import ActionAgent
from app.core.memory import MemoryManager, ConversationMemory
from app.utils.guardrails import Guardrails
from app.utils.evaluator import ResponseEvaluator
from app.models.schemas import SourceDocument


class TestConversationMemory:
    def test_add_message(self):
        memory = ConversationMemory("test-session")
        memory.add_message("user", "Hello")
        assert len(memory) == 1

    def test_get_history(self):
        memory = ConversationMemory("test-session")
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")
        history = memory.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"

    def test_max_items(self):
        memory = ConversationMemory("test-session", max_items=3)
        for i in range(5):
            memory.add_message("user", f"Message {i}")
        assert len(memory) == 3

    def test_clear(self):
        memory = ConversationMemory("test-session")
        memory.add_message("user", "Hello")
        memory.clear()
        assert len(memory) == 0

    def test_formatted_history(self):
        memory = ConversationMemory("test-session")
        memory.add_message("user", "Hello")
        formatted = memory.get_formatted_history()
        assert "USER" in formatted
        assert "Hello" in formatted


class TestMemoryManager:
    def test_get_session_memory(self):
        manager = MemoryManager()
        memory = manager.get_session_memory("session-1")
        assert isinstance(memory, ConversationMemory)

    def test_singleton(self):
        manager1 = MemoryManager()
        manager2 = MemoryManager()
        assert manager1 is manager2

    def test_delete_session(self):
        manager = MemoryManager()
        manager.get_session_memory("test-delete")
        manager.delete_session("test-delete")
        assert "test-delete" not in manager.list_sessions()


class TestGuardrails:
    def test_valid_input(self):
        guardrails = Guardrails()
        result = guardrails.validate_input("What are the compliance requirements?")
        assert result["is_valid"] is True

    def test_empty_input(self):
        guardrails = Guardrails()
        result = guardrails.validate_input("")
        assert result["is_valid"] is False

    def test_too_long_input(self):
        guardrails = Guardrails()
        result = guardrails.validate_input("x" * 15000)
        assert result["is_valid"] is False

    def test_valid_output(self):
        guardrails = Guardrails()
        result = guardrails.validate_output("This is a valid response.")
        assert result["is_valid"] is True

    def test_pii_detection(self):
        guardrails = Guardrails()
        result = guardrails.detect_pii("My SSN is 123-45-6789")
        assert result["has_pii"] is True


class TestResponseEvaluator:
    def test_evaluate_relevance(self):
        evaluator = ResponseEvaluator()
        score = evaluator.evaluate_relevance(
            "What is compliance?",
            "Compliance refers to following rules and regulations.",
            ["Compliance is the adherence to rules."],
        )
        assert 0 <= score <= 1

    def test_evaluate_completeness(self):
        evaluator = ResponseEvaluator()
        short_score = evaluator.evaluate_completeness("Short")
        long_score = evaluator.evaluate_completeness("This is a much longer and more detailed response " * 20)
        assert long_score > short_score

    def test_evaluate_response(self):
        evaluator = ResponseEvaluator()
        result = evaluator.evaluate_response(
            query="What is GDPR?",
            response="GDPR is the General Data Protection Regulation for EU data privacy.",
            source_docs=["GDPR is a regulation in EU law on data protection."],
        )
        assert "overall_score" in result
        assert "quality_tier" in result


@pytest.mark.asyncio
class TestRetrievalAgent:
    async def test_retrieve_empty_store(self, mock_vector_store):
        agent = RetrievalAgent(mock_vector_store)
        results = await agent.retrieve("test query")
        assert results == []

    async def test_retrieve_with_results(self, mock_vector_store):
        from langchain_core.documents import Document
        mock_doc = Document(
            page_content="Test content",
            metadata={"document_id": "doc-1", "filename": "test.pdf"},
        )
        mock_vector_store.similarity_search.return_value = [(mock_doc, 0.85)]
        agent = RetrievalAgent(mock_vector_store)
        results = await agent.retrieve("test query")
        assert len(results) == 1
        assert results[0].document_id == "doc-1"


@pytest.mark.asyncio
class TestReasoningAgent:
    async def test_reason_no_docs(self, mock_llm_service):
        manager = MemoryManager()
        agent = ReasoningAgent(mock_llm_service, manager)
        result = await agent.reason("test query", [])
        assert "answer" in result
        assert "confidence" in result

    async def test_reason_with_docs(self, mock_llm_service):
        manager = MemoryManager()
        agent = ReasoningAgent(mock_llm_service, manager)
        docs = [
            SourceDocument(
                document_id="doc-1",
                filename="test.pdf",
                content="Test content about compliance",
                score=0.9,
            )
        ]
        result = await agent.reason("What is this about?", docs, session_id="test-session")
        assert "answer" in result
        assert result["confidence"] >= 0
