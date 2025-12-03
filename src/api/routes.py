"""API routes for feedback analysis endpoints."""

from typing import Dict

from fastapi import APIRouter, HTTPException, status

from src.agents.orchestrator import get_orchestrator
from src.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse,
    FeedbackUploadRequest,
    FeedbackUploadResponse,
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post(
    "/upload",
    response_model=FeedbackUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Feedback",
    description="Upload feedback data for analysis",
)
async def upload_feedback(request: FeedbackUploadRequest) -> FeedbackUploadResponse:
    """
    Upload feedback data.

    Args:
        request: Feedback upload request with list of feedback texts

    Returns:
        FeedbackUploadResponse: Upload confirmation with feedback ID

    Raises:
        HTTPException: If upload fails
    """
    logger.info(f"Received feedback upload request with {len(request.feedback)} items")

    try:
        orchestrator = get_orchestrator()

        # Process feedback through ingestion only
        result = orchestrator.ingestion_agent.ingest_feedback(
            feedback=request.feedback,
            metadata=request.metadata,
        )

        if not result["success"]:
            logger.error(f"Feedback upload failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Upload failed"),
            )

        feedback_id = result["feedback_id"]
        ingested_count = result["ingested_count"]

        logger.info(f"Feedback uploaded successfully: {feedback_id}")

        return FeedbackUploadResponse(
            feedback_id=feedback_id,
            status="success",
            count=ingested_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/analyze",
    response_model=Dict,
    summary="Analyze Feedback",
    description="Analyze uploaded feedback and generate comprehensive report",
)
async def analyze_feedback(request: AnalysisRequest) -> Dict:
    """
    Analyze uploaded feedback.

    Args:
        request: Analysis request with feedback ID

    Returns:
        Dict: Complete analysis results with sentiment, topics, and insights

    Raises:
        HTTPException: If analysis fails or feedback ID not found
    """
    logger.info(f"Received analysis request for feedback_id: {request.feedback_id}")

    try:
        orchestrator = get_orchestrator()

        # Run analysis on existing feedback
        result = orchestrator.analyze_existing_feedback(
            feedback_id=request.feedback_id,
            options=request.options,
        )

        if not result["success"]:
            logger.error(f"Analysis failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                if "not found" in result.get("error", "").lower()
                else status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Analysis failed"),
            )

        logger.info(f"Analysis completed for feedback_id: {request.feedback_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post(
    "/process",
    response_model=Dict,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Analyze",
    description="Upload feedback and immediately analyze it (combined operation)",
)
async def process_feedback(request: FeedbackUploadRequest) -> Dict:
    """
    Upload and analyze feedback in one operation.

    Args:
        request: Feedback upload request

    Returns:
        Dict: Complete analysis results

    Raises:
        HTTPException: If processing fails
    """
    logger.info(
        f"Received combined process request with {len(request.feedback)} items"
    )

    try:
        orchestrator = get_orchestrator()

        # Process complete pipeline
        result = orchestrator.process_feedback(
            feedback=request.feedback,
            metadata=request.metadata,
            options={"include_summary": True, "include_topics": True},
        )

        if not result["success"]:
            logger.error(f"Processing failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Processing failed"),
            )

        logger.info(f"Processing completed: {result.get('feedback_id')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/feedback/{feedback_id}",
    response_model=Dict,
    summary="Get Feedback Summary",
    description="Get summary of uploaded feedback batch",
)
async def get_feedback_summary(feedback_id: str) -> Dict:
    """
    Get feedback batch summary.

    Args:
        feedback_id: Feedback batch ID

    Returns:
        Dict: Feedback summary with representative samples

    Raises:
        HTTPException: If feedback ID not found
    """
    logger.info(f"Received request for feedback summary: {feedback_id}")

    try:
        orchestrator = get_orchestrator()

        result = orchestrator.get_feedback_summary(feedback_id)

        if not result["success"]:
            logger.error(f"Failed to get summary: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Feedback not found"),
            )

        logger.info(f"Retrieved summary for: {feedback_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/statistics",
    response_model=Dict,
    summary="Get System Statistics",
    description="Get overall system statistics",
)
async def get_statistics() -> Dict:
    """
    Get system statistics.

    Returns:
        Dict: System statistics including document counts

    Raises:
        HTTPException: If retrieval fails
    """
    logger.info("Received request for system statistics")

    try:
        orchestrator = get_orchestrator()

        stats = orchestrator.ingestion_agent.get_statistics()

        return {
            "success": True,
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
