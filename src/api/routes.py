"""API routes for feedback analysis endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.agents.orchestrator import get_orchestrator
from src.db.database import get_db
from src.db.models import User
from src.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse,
    FeedbackUploadRequest,
    FeedbackUploadResponse,
)
from src.services.auth import get_current_user
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
async def upload_feedback(
    request: FeedbackUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FeedbackUploadResponse:
    """
    Upload feedback data.

    Args:
        request: Feedback upload request with list of feedback texts
        current_user: Authenticated user
        db: Database session

    Returns:
        FeedbackUploadResponse: Upload confirmation with feedback ID

    Raises:
        HTTPException: If upload fails
    """
    logger.info(f"User {current_user.username} uploading {len(request.feedback)} feedback entries")

    try:
        orchestrator = get_orchestrator()

        # Process feedback through ingestion with database persistence
        result = orchestrator.ingestion_agent.ingest_feedback(
            feedback=request.feedback,
            metadata=request.metadata,
            user_id=current_user.id,
            batch_name=request.batch_name,
            description=request.description,
            db=db,
        )

        if not result["success"]:
            logger.error(f"Feedback upload failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Upload failed"),
            )

        feedback_id = result["feedback_id"]
        ingested_count = result["ingested_count"]

        logger.info(f"Feedback uploaded successfully: {feedback_id} by user {current_user.username}")

        return FeedbackUploadResponse(
            feedback_id=feedback_id,
            user_id=current_user.id,
            status="success",
            count=ingested_count,
            batch_name=request.batch_name,
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
async def analyze_feedback(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze uploaded feedback.

    Args:
        request: Analysis request with feedback ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Dict: Complete analysis results with emotions, topics, and insights

    Raises:
        HTTPException: If analysis fails or feedback ID not found
    """
    logger.info(f"User {current_user.username} analyzing feedback_id: {request.feedback_id}")

    try:
        orchestrator = get_orchestrator()

        # Run analysis on existing feedback with database persistence
        result = orchestrator.analyze_existing_feedback(
            feedback_id=request.feedback_id,
            options=request.options,
            user_id=current_user.id,
            db=db,
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
async def process_feedback(
    request: FeedbackUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and analyze feedback in one operation.

    Args:
        request: Feedback upload request
        current_user: Authenticated user
        db: Database session

    Returns:
        Dict: Complete analysis results

    Raises:
        HTTPException: If processing fails
    """
    logger.info(
        f"User {current_user.username} processing {len(request.feedback)} feedback entries"
    )

    try:
        orchestrator = get_orchestrator()

        # Process complete pipeline with database persistence
        result = orchestrator.process_feedback(
            feedback=request.feedback,
            metadata=request.metadata,
            user_id=current_user.id,
            batch_name=request.batch_name,
            description=request.description,
            db=db,
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
async def get_feedback_summary(
    feedback_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
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
    description="Get overall system statistics for current user",
)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get system statistics for current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dict: User statistics including document counts and feedback batches

    Raises:
        HTTPException: If retrieval fails
    """
    logger.info(f"Retrieving statistics for user: {current_user.username}")

    try:
        from src.db.models import FeedbackBatch, AnalysisResult

        # Get user-specific statistics from database
        total_batches = db.query(FeedbackBatch).filter(
            FeedbackBatch.user_id == current_user.id
        ).count()

        total_feedback = db.query(FeedbackBatch).filter(
            FeedbackBatch.user_id == current_user.id
        ).with_entities(FeedbackBatch.total_count).all()
        total_feedback_count = sum([count[0] for count in total_feedback])

        total_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == current_user.id
        ).count()

        return {
            "success": True,
            "statistics": {
                "total_batches": total_batches,
                "total_feedback": total_feedback_count,
                "total_analyses": total_analyses,
                "user_id": current_user.id,
                "username": current_user.username,
            },
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/history/emotions",
    response_model=Dict,
    summary="Get Emotion Analysis History",
    description="Get historical emotion analysis results for the current user",
)
async def get_emotion_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
) -> Dict:
    """
    Get emotion analysis history for current user.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of results to return (default: 10)

    Returns:
        Dict: Historical emotion analysis results

    Raises:
        HTTPException: If retrieval fails
    """
    logger.info(f"Retrieving emotion history for user: {current_user.username}")

    try:
        from src.db.models import FeedbackBatch, AnalysisResult

        # Get analysis results for user, ordered by creation date (newest first)
        analyses = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == current_user.id
        ).order_by(
            AnalysisResult.created_at.desc()
        ).limit(limit).all()

        # Format results
        history = []
        for analysis in analyses:
            # Get associated feedback batch info
            batch = db.query(FeedbackBatch).filter(
                FeedbackBatch.id == analysis.feedback_batch_id
            ).first()

            # Extract emotion data
            emotion_data = analysis.emotion_scores or {}
            average_scores = emotion_data.get("average_scores", {})
            emotion_distribution = emotion_data.get("emotion_distribution", {})
            dominant_emotion = emotion_data.get("dominant_emotion", "neutral")

            history.append({
                "analysis_id": analysis.id,
                "feedback_batch_id": analysis.feedback_batch_id,
                "batch_name": batch.name if batch else None,
                "created_at": analysis.created_at.isoformat(),
                "emotion_scores": {
                    "average_scores": average_scores,
                    "emotion_distribution": emotion_distribution,
                    "dominant_emotion": dominant_emotion
                },
                "feedback_count": batch.total_count if batch else 0
            })

        return {
            "success": True,
            "count": len(history),
            "history": history,
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error(f"Error getting emotion history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/history/emotions/aggregate",
    response_model=Dict,
    summary="Get Aggregated Emotion History",
    description="Get aggregated emotion statistics across all user's analyses",
)
async def get_aggregated_emotion_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get aggregated emotion statistics across all analyses for current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dict: Aggregated emotion statistics

    Raises:
        HTTPException: If retrieval fails
    """
    logger.info(f"Retrieving aggregated emotion history for user: {current_user.username}")

    try:
        from src.db.models import AnalysisResult

        # Get all analysis results for user
        analyses = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == current_user.id
        ).all()

        if not analyses:
            return {
                "success": True,
                "message": "No analysis history found",
                "total_analyses": 0,
                "aggregated_emotions": {
                    "joy": 0.0,
                    "sadness": 0.0,
                    "anger": 0.0,
                    "fear": 0.0,
                    "surprise": 0.0,
                    "neutral": 0.0
                },
                "emotion_distribution_total": {
                    "joy": 0,
                    "sadness": 0,
                    "anger": 0,
                    "fear": 0,
                    "surprise": 0,
                    "neutral": 0
                }
            }

        # Aggregate emotion scores
        emotion_sum = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "neutral": 0.0
        }

        emotion_distribution_total = {
            "joy": 0,
            "sadness": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0,
            "neutral": 0
        }

        for analysis in analyses:
            emotion_data = analysis.emotion_scores or {}
            average_scores = emotion_data.get("average_scores", {})
            distribution = emotion_data.get("emotion_distribution", {})

            # Sum average scores
            for emotion in emotion_sum.keys():
                emotion_sum[emotion] += average_scores.get(emotion, 0.0)
                emotion_distribution_total[emotion] += distribution.get(emotion, 0)

        # Calculate averages
        num_analyses = len(analyses)
        aggregated_emotions = {
            emotion: score / num_analyses
            for emotion, score in emotion_sum.items()
        }

        return {
            "success": True,
            "total_analyses": num_analyses,
            "aggregated_emotions": aggregated_emotions,
            "emotion_distribution_total": emotion_distribution_total,
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error(f"Error getting aggregated emotion history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get(
    "/history/analyses",
    response_model=Dict,
    summary="Get Full Analysis History",
    description="Get historical analysis results (emotions + topics) for the current user",
)
async def get_full_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
) -> Dict:
    """
    Get full analysis history for current user.
    Returns emotion_scores and topic_results for each analysis.
    """
    logger.info(f"Retrieving full analysis history for user: {current_user.username}")

    try:
        from src.db.models import AnalysisResult, FeedbackBatch

        analyses = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == current_user.id
        ).order_by(AnalysisResult.created_at.desc()).limit(limit).all()

        history = []
        for analysis in analyses:
            batch = db.query(FeedbackBatch).filter(FeedbackBatch.id == analysis.feedback_batch_id).first()

            history.append({
                "analysis_id": analysis.id,
                "feedback_batch_id": analysis.feedback_batch_id,
                "batch_name": batch.name if batch else None,
                "created_at": analysis.created_at.isoformat(),
                "emotion_scores": analysis.emotion_scores or {},
                "topic_results": analysis.topic_results or {},
                "summary": analysis.summary,
                "feedback_count": batch.total_count if batch else 0,
            })

        return {
            "success": True,
            "count": len(history),
            "history": history,
            "user_id": current_user.id,
        }

    except Exception as e:
        logger.error(f"Error getting full analysis history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
