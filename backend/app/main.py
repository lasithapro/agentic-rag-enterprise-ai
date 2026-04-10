"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_logger
from app.api.routes import documents, query, reports, health

# Setup logging before everything
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

# Ensure data directories exist
os.makedirs("./data/uploads", exist_ok=True)
os.makedirs("./data/vector_store", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info("Starting Agentic RAG Enterprise AI", version=settings.APP_VERSION)
    # Pre-initialize the orchestrator singleton
    from app.agents.orchestrator import AgentOrchestrator
    AgentOrchestrator.get_instance()
    logger.info("All agents initialized successfully")
    yield
    logger.info("Shutting down Agentic RAG Enterprise AI")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Agentic RAG Enterprise AI
    
    A production-ready multi-agent system for enterprise document analysis.
    
    ### Features
    - **Document Ingestion**: PDF, Word, Text, and Web content
    - **RAG Pipeline**: Semantic search with FAISS vector database
    - **AI Reasoning**: Powered by Google Gemini LLM
    - **Action Agents**: Summarization, compliance validation, report generation
    - **Memory**: Conversation history management
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(documents.router, prefix=settings.API_PREFIX)
app.include_router(query.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": f"{settings.API_PREFIX}/health",
    }
