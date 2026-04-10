"""LLM service using Google Gemini."""
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """Service for interacting with Google Gemini LLM."""

    def __init__(self):
        self._client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
            if settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self._client = genai.GenerativeModel(
                    model_name=settings.LLM_MODEL,
                    generation_config={
                        "temperature": settings.LLM_TEMPERATURE,
                        "max_output_tokens": settings.LLM_MAX_TOKENS,
                        "top_p": 0.95,
                    },
                )
                logger.info("Initialized Gemini LLM client", model=settings.LLM_MODEL)
            else:
                logger.warning("No GOOGLE_API_KEY provided, LLM service will use mock responses")
        except Exception as e:
            logger.error("Failed to initialize LLM client", error=str(e))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the LLM."""
        if self._client is None:
            return self._mock_response(prompt)

        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            response = self._client.generate_content(full_prompt)
            result = response.text
            logger.debug("LLM generation completed", prompt_length=len(prompt))
            return result
        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            raise

    def _mock_response(self, prompt: str) -> str:
        """Return a mock response when LLM is not configured."""
        return (
            "This is a mock response. Please configure GOOGLE_API_KEY "
            "to enable real LLM responses. Your query was: " + prompt[:100]
        )

    async def generate_with_context(
        self,
        query: str,
        context_documents: List[str],
        conversation_history: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate response with retrieved context documents."""
        context = "\n\n---\n\n".join(context_documents)
        history_section = ""
        if conversation_history:
            history_section = f"\n\nConversation History:\n{conversation_history}"

        prompt = f"""Based on the following context documents, answer the user's question accurately and comprehensively.

Context Documents:
{context}
{history_section}

User Question: {query}

Instructions:
1. Answer based primarily on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Cite specific parts of the context when relevant
4. Be precise and factual
5. Structure your response clearly

Answer:"""

        if system_prompt is None:
            system_prompt = """You are an expert enterprise AI assistant specializing in document analysis, 
compliance validation, and knowledge extraction. You provide accurate, well-structured responses 
based on the documents provided to you."""

        response = await self.generate(prompt, system_prompt)
        confidence = self._estimate_confidence(response, context_documents)
        return {
            "answer": response,
            "confidence": confidence,
        }

    def _estimate_confidence(self, response: str, context_docs: List[str]) -> float:
        """Estimate confidence score based on response quality indicators."""
        confidence = 0.7
        uncertainty_phrases = ["I don't know", "not sure", "unclear", "insufficient information", "cannot determine"]
        for phrase in uncertainty_phrases:
            if phrase.lower() in response.lower():
                confidence -= 0.2
        if len(response) > 200:
            confidence += 0.1
        if context_docs:
            confidence += min(len(context_docs) * 0.02, 0.1)
        return max(0.1, min(1.0, confidence))
