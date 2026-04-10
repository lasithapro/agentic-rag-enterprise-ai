"""Reasoning Agent - LLM-powered contextual understanding."""
import time
from typing import List, Optional, Dict, Any
from app.services.llm_service import LLMService
from app.core.memory import MemoryManager
from app.models.schemas import QueryResponse, SourceDocument
from app.core.logging_config import get_logger
from app.utils.guardrails import Guardrails

logger = get_logger(__name__)


SYSTEM_PROMPT = """You are an expert enterprise AI assistant specializing in:
- Document analysis and comprehension
- Policy and compliance validation
- Knowledge extraction and synthesis
- Business intelligence and insights

Guidelines:
1. Always base your answers on the provided context documents
2. Be precise, factual, and cite sources when possible
3. Acknowledge uncertainty when information is insufficient
4. Structure responses clearly with appropriate formatting
5. Flag potential compliance or risk issues proactively
6. Maintain professional, business-appropriate tone"""


class ReasoningAgent:
    """
    Reasoning Agent responsible for:
    - Contextual understanding using LLM
    - Multi-step reasoning and decision making
    - Conversation memory management
    - Response generation with proper attribution
    """

    def __init__(self, llm_service: LLMService, memory_manager: MemoryManager):
        self.llm = llm_service
        self.memory = memory_manager
        self.guardrails = Guardrails()
        logger.info("ReasoningAgent initialized")

    async def reason(
        self,
        query: str,
        source_docs: List[SourceDocument],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a reasoned response based on retrieved documents."""
        start_time = time.time()
        logger.info("Starting reasoning", query=query[:50], docs=len(source_docs))

        # Get conversation history
        conversation_history = None
        if session_id:
            session_memory = self.memory.get_session_memory(session_id)
            conversation_history = session_memory.get_formatted_history(limit=5)
            session_memory.add_message("user", query)

        # Validate query with guardrails
        query_check = self.guardrails.validate_input(query)
        if not query_check["is_valid"]:
            response_text = f"I cannot process this request: {query_check['reason']}"
            if session_id:
                session_memory = self.memory.get_session_memory(session_id)
                session_memory.add_message("assistant", response_text)
            return {
                "answer": response_text,
                "confidence": 0.0,
                "reasoning_steps": ["Input validation failed"],
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

        context_texts = [doc.content for doc in source_docs]
        reasoning_steps = []
        reasoning_steps.append(f"Retrieved {len(source_docs)} relevant document chunks")

        if not source_docs:
            reasoning_steps.append("No relevant documents found in the knowledge base")
            response_text = (
                "I couldn't find relevant information in the knowledge base to answer your question. "
                "Please ensure relevant documents have been uploaded, or rephrase your query."
            )
            confidence = 0.1
        else:
            reasoning_steps.append("Analyzing retrieved context for relevance")
            result = await self.llm.generate_with_context(
                query=query,
                context_documents=context_texts,
                conversation_history=conversation_history,
                system_prompt=SYSTEM_PROMPT,
            )
            response_text = result["answer"]
            confidence = result["confidence"]
            reasoning_steps.append("Generated response using LLM with context")

            # Validate output with guardrails
            output_check = self.guardrails.validate_output(response_text)
            if not output_check["is_valid"]:
                reasoning_steps.append("Output guardrail triggered, applying safety filter")
                response_text = output_check.get("sanitized", response_text)

        # Update memory with response
        if session_id:
            session_memory = self.memory.get_session_memory(session_id)
            session_memory.add_message("assistant", response_text)

        elapsed_ms = (time.time() - start_time) * 1000
        reasoning_steps.append(f"Completed reasoning in {elapsed_ms:.0f}ms")

        logger.info("Reasoning completed", confidence=confidence, elapsed_ms=elapsed_ms)

        return {
            "answer": response_text,
            "confidence": confidence,
            "reasoning_steps": reasoning_steps,
            "processing_time_ms": elapsed_ms,
        }
