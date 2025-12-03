"""FastAPI application for NLP Agentic AI Feedback Analysis System."""

from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.utils.config import get_config
from src.utils.logging_config import get_logger, setup_logging

# Initialize logging
config = get_config()
setup_logging(
    log_level=config.logging.level,
    log_format=config.logging.format,
    log_file=config.logging.log_file,
    max_file_size=config.logging.max_file_size,
    backup_count=config.logging.backup_count,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting NLP Agentic AI Feedback Analysis System")
    logger.info(f"Configuration loaded from: {config}")

    # Initialize services (lazy loading will happen on first use)
    from src.services.embeddings import get_embedding_service
    from src.services.vectorstore import get_vector_store_service

    try:
        # Pre-load services to ensure they're ready
        logger.info("Initializing embedding service...")
        embedding_service = get_embedding_service()
        logger.info(f"Embedding service ready: {embedding_service.get_model_info()}")

        logger.info("Initializing vector store service...")
        vector_store = get_vector_store_service()
        logger.info(f"Vector store ready: {vector_store.get_stats()}")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down NLP Agentic AI Feedback Analysis System")


# Create FastAPI app
app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns:
        Dict[str, str]: Welcome message
    """
    return {
        "message": "Welcome to NLP Agentic AI Feedback Analysis System",
        "version": config.api.version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    from src.services.embeddings import get_embedding_service
    from src.services.vectorstore import get_vector_store_service

    try:
        # Check embedding service
        embedding_service = get_embedding_service()
        embedding_info = embedding_service.get_model_info()

        # Check vector store
        vector_store = get_vector_store_service()
        vector_store_stats = vector_store.get_stats()

        return {
            "status": "healthy",
            "embedding_service": "operational",
            "embedding_model": embedding_info["model_name"],
            "vector_store": "operational",
            "document_count": str(vector_store_stats["document_count"]),
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@app.get("/info")
async def system_info() -> Dict:
    """
    Get system information.

    Returns:
        Dict: System information including configuration
    """
    from src.services.embeddings import get_embedding_service
    from src.services.vectorstore import get_vector_store_service

    embedding_service = get_embedding_service()
    vector_store = get_vector_store_service()

    return {
        "api": {
            "title": config.api.title,
            "version": config.api.version,
            "description": config.api.description,
        },
        "embedding_service": embedding_service.get_model_info(),
        "vector_store": vector_store.get_stats(),
        "configuration": {
            "log_level": config.logging.level,
            "agent_timeout": config.agents.timeout,
            "max_topics": config.nlp.max_topics,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=True,
        log_level=config.logging.level.lower(),
    )
