"""FAISS vector store service for document embeddings."""
import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VectorStoreService:
    """Manages FAISS vector store for document embeddings."""

    def __init__(self):
        self.store_path = Path(settings.VECTOR_STORE_PATH)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self._vector_store: Optional[FAISS] = None
        self._document_metadata: Dict[str, Dict] = {}
        self._metadata_file = self.store_path / "metadata.json"
        self._load_metadata()
        self._load_or_create_store()

    def _load_metadata(self) -> None:
        """Load document metadata from disk."""
        if self._metadata_file.exists():
            with open(self._metadata_file, "r") as f:
                self._document_metadata = json.load(f)
            logger.info("Loaded document metadata", count=len(self._document_metadata))

    def _save_metadata(self) -> None:
        """Save document metadata to disk."""
        with open(self._metadata_file, "w") as f:
            json.dump(self._document_metadata, f, indent=2)

    def _load_or_create_store(self) -> None:
        """Load existing FAISS store or create a new one."""
        index_file = self.store_path / "index.faiss"
        if index_file.exists():
            try:
                self._vector_store = FAISS.load_local(
                    str(self.store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info("Loaded existing FAISS vector store")
            except Exception as e:
                logger.warning("Failed to load FAISS store, creating new", error=str(e))
                self._vector_store = None
        else:
            logger.info("No existing vector store found, will create on first document")

    def add_documents(
        self, documents: List[Document], document_id: str, filename: str
    ) -> int:
        """Add documents to the vector store."""
        if not documents:
            return 0

        try:
            if self._vector_store is None:
                self._vector_store = FAISS.from_documents(documents, self.embeddings)
            else:
                self._vector_store.add_documents(documents)

            self._vector_store.save_local(str(self.store_path))
            self._document_metadata[document_id] = {
                "filename": filename,
                "chunk_count": len(documents),
                "document_type": documents[0].metadata.get("document_type", "unknown"),
            }
            self._save_metadata()
            logger.info("Added documents to vector store", document_id=document_id, chunks=len(documents))
            return len(documents)
        except Exception as e:
            logger.error("Failed to add documents to vector store", error=str(e))
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        document_ids: Optional[List[str]] = None,
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if self._vector_store is None:
            logger.warning("Vector store is empty, no results to return")
            return []

        try:
            results = self._vector_store.similarity_search_with_score(query, k=k * 2)
            if document_ids:
                results = [
                    (doc, score)
                    for doc, score in results
                    if doc.metadata.get("document_id") in document_ids
                ]
            results = results[:k]
            logger.debug("Similarity search completed", query=query[:50], results=len(results))
            return results
        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            raise

    def get_document_info(self, document_id: str) -> Optional[Dict]:
        """Get metadata for a specific document."""
        return self._document_metadata.get(document_id)

    def list_documents(self) -> List[Dict]:
        """List all documents in the store."""
        return [
            {"document_id": doc_id, **meta}
            for doc_id, meta in self._document_metadata.items()
        ]

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from metadata (full FAISS rebuild not implemented)."""
        if document_id in self._document_metadata:
            del self._document_metadata[document_id]
            self._save_metadata()
            logger.info("Deleted document metadata", document_id=document_id)
            return True
        return False

    @property
    def document_count(self) -> int:
        """Get total number of indexed documents."""
        return len(self._document_metadata)
