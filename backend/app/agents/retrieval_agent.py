"""Retrieval Agent - RAG pipeline with vector database."""
import time
from typing import List, Optional
from langchain_core.documents import Document
from app.services.vector_store import VectorStoreService
from app.models.schemas import SourceDocument
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RetrievalAgent:
    """
    Retrieval Agent responsible for:
    - Semantic search using FAISS vector store
    - Relevance scoring and filtering
    - Context window management
    - Document ranking and selection
    """

    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        logger.info("RetrievalAgent initialized")

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        min_score: float = 0.0,
    ) -> List[SourceDocument]:
        """Retrieve relevant documents for a query."""
        start_time = time.time()
        logger.info("Retrieving documents", query=query[:50], top_k=top_k)

        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=top_k,
                document_ids=document_ids,
            )

            source_docs = []
            for doc, score in results:
                if score >= min_score:
                    source_docs.append(
                        SourceDocument(
                            document_id=doc.metadata.get("document_id", "unknown"),
                            filename=doc.metadata.get("filename", doc.metadata.get("url", "unknown")),
                            content=doc.page_content,
                            score=float(score),
                            page_number=doc.metadata.get("page_number"),
                        )
                    )

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                "Document retrieval completed",
                results=len(source_docs),
                elapsed_ms=elapsed_ms,
            )
            return source_docs

        except Exception as e:
            logger.error("Document retrieval failed", error=str(e))
            raise

    def get_context_texts(self, source_docs: List[SourceDocument]) -> List[str]:
        """Extract text content from source documents for LLM context."""
        return [doc.content for doc in source_docs]
