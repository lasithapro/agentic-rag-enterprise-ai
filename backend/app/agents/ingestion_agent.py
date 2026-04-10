"""Data Ingestion Agent - handles document ingestion from multiple sources."""
import time
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.models.schemas import DocumentUploadResponse, WebIngestionResponse, DocumentType, ProcessingStatus
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class IngestionAgent:
    """
    Data Ingestion Agent responsible for:
    - Processing PDF, Word, and text documents
    - Fetching and processing web content
    - Chunking and embedding documents
    - Storing in vector database
    """

    def __init__(self, doc_processor: DocumentProcessor, vector_store: VectorStoreService):
        self.doc_processor = doc_processor
        self.vector_store = vector_store
        logger.info("IngestionAgent initialized")

    async def ingest_file(self, file: UploadFile) -> DocumentUploadResponse:
        """Ingest a file (PDF, Word, or text) into the vector store."""
        start_time = time.time()
        filename = file.filename or "unknown"
        extension = Path(filename).suffix.lower()

        doc_type_map = {
            ".pdf": DocumentType.PDF,
            ".doc": DocumentType.WORD,
            ".docx": DocumentType.WORD,
            ".txt": DocumentType.TEXT,
            ".md": DocumentType.TEXT,
        }
        document_type = doc_type_map.get(extension, DocumentType.TEXT)

        try:
            logger.info("Starting file ingestion", filename=filename, document_type=document_type)
            document_id, file_path = await self.doc_processor.save_upload_file(file)
            chunks = self.doc_processor.process_file(file_path, document_id, filename)
            chunks_count = self.vector_store.add_documents(chunks, document_id, filename)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                "File ingestion completed",
                document_id=document_id,
                filename=filename,
                chunks=chunks_count,
                elapsed_ms=elapsed_ms,
            )

            return DocumentUploadResponse(
                document_id=document_id,
                filename=filename,
                document_type=document_type,
                status=ProcessingStatus.COMPLETED,
                message=f"Successfully ingested {filename} with {chunks_count} chunks",
                chunks_created=chunks_count,
            )
        except Exception as e:
            logger.error("File ingestion failed", filename=filename, error=str(e))
            return DocumentUploadResponse(
                document_id="",
                filename=filename,
                document_type=document_type,
                status=ProcessingStatus.FAILED,
                message=f"Ingestion failed: {str(e)}",
                chunks_created=0,
            )

    async def ingest_web_url(self, url: str) -> WebIngestionResponse:
        """Ingest content from a web URL into the vector store."""
        import uuid
        start_time = time.time()
        document_id = str(uuid.uuid4())

        try:
            logger.info("Starting web URL ingestion", url=url)
            chunks = await self.doc_processor.process_web_url(url, document_id)
            chunks_count = self.vector_store.add_documents(chunks, document_id, url)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                "Web URL ingestion completed",
                document_id=document_id,
                url=url,
                chunks=chunks_count,
                elapsed_ms=elapsed_ms,
            )

            return WebIngestionResponse(
                document_id=document_id,
                url=url,
                status=ProcessingStatus.COMPLETED,
                message=f"Successfully ingested content from {url} with {chunks_count} chunks",
                chunks_created=chunks_count,
            )
        except Exception as e:
            logger.error("Web URL ingestion failed", url=url, error=str(e))
            return WebIngestionResponse(
                document_id=document_id,
                url=url,
                status=ProcessingStatus.FAILED,
                message=f"Web ingestion failed: {str(e)}",
                chunks_created=0,
            )
