"""Agent Orchestrator - Coordinates multi-agent workflow."""

from typing import Dict, List, Optional

from src.agents.analysis_agent import get_analysis_agent
from src.agents.data_ingestion_agent import get_data_ingestion_agent
from src.agents.retrieval_agent import get_retrieval_agent
from src.agents.synthesis_agent import get_synthesis_agent
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent workflow for feedback analysis."""

    def __init__(self):
        """Initialize Agent Orchestrator."""
        self.config = get_config()

        # Initialize all agents
        self.ingestion_agent = get_data_ingestion_agent()
        self.analysis_agent = get_analysis_agent()
        self.retrieval_agent = get_retrieval_agent()
        self.synthesis_agent = get_synthesis_agent()

        logger.info("Agent Orchestrator initialized with all 4 agents")

    def process_feedback(
        self,
        feedback: List[str],
        metadata: Optional[List[Dict]] = None,
        options: Optional[Dict] = None,
        user_id: Optional[str] = None,
        batch_name: Optional[str] = None,
        description: Optional[str] = None,
        db=None,
    ) -> Dict:
        """
        Complete feedback processing pipeline.

        Args:
            feedback: List of feedback texts
            metadata: Optional metadata for each feedback
            options: Optional processing options

        Returns:
            Dict: Complete analysis results
        """
        logger.info(f"Starting feedback processing pipeline for {len(feedback)} items")

        options = options or {}
        include_summary = options.get("include_summary", True)
        include_topics = options.get("include_topics", True)
        include_rag = options.get("include_rag", False)
        include_absa = options.get("include_absa", True)  # ABSA enabled by default

        try:
            with LogExecutionTime(logger, "Complete feedback processing"):
                # Step 1: Data Ingestion
                logger.info("Step 1/4: Data Ingestion")
                ingestion_result = self.ingestion_agent.ingest_feedback(
                    feedback=feedback,
                    metadata=metadata,
                    user_id=user_id,
                    batch_name=batch_name,
                    description=description,
                    db=db,
                )

                if not ingestion_result["success"]:
                    return {
                        "success": False,
                        "error": "Data ingestion failed",
                        "details": ingestion_result,
                    }

                feedback_id = ingestion_result["feedback_id"]
                cleaned_texts = ingestion_result["validation"]["cleaned_texts"]

                logger.info(f"Ingestion complete: {len(cleaned_texts)} valid texts")

                # Step 2: Analysis (Emotions + Topics + ABSA)
                logger.info(f"Step 2/4: Analysis (Emotions + Topics + {'ABSA' if include_absa else 'no ABSA'})")
                analysis_result = self.analysis_agent.analyze(
                    texts=cleaned_texts,
                    include_topics=include_topics,
                    include_emotions=True,
                    include_absa=include_absa,  # Include ABSA
                )

                logger.info("Analysis complete")

                # Step 3: RAG Retrieval (Optional)
                rag_context = None
                if include_rag and analysis_result.get("topics"):
                    logger.info("Step 3/4: RAG Retrieval")
                    topics = analysis_result["topics"].get("topics", [])
                    if topics:
                        rag_context = self.retrieval_agent.retrieve_context_for_topics(
                            topics=topics,
                            n_results_per_topic=3,
                            feedback_id=feedback_id,
                        )
                        logger.info("RAG retrieval complete")
                else:
                    logger.info("Step 3/4: RAG Retrieval (skipped)")

                # Step 4: Synthesis
                logger.info("Step 4/4: Synthesis")

                # Get additional insights from analysis agent
                additional_insights = self.analysis_agent.get_insights(analysis_result)

                # Generate comprehensive report
                report = self.synthesis_agent.synthesize_report(
                    feedback_id=feedback_id,
                    texts=cleaned_texts,
                    emotion_results=analysis_result.get("emotions", {}),
                    topic_results=analysis_result.get("topics", {}),
                    additional_insights=additional_insights,
                )

                # Add summary if requested
                if include_summary:
                    summary = self.synthesis_agent.generate_summary(cleaned_texts)
                    report["summary"] = summary

                logger.info("Synthesis complete")

                # Save analysis results to database if user_id and db provided
                if user_id and db:
                    try:
                        from src.db.models import AnalysisResult

                        analysis_record = AnalysisResult(
                            feedback_batch_id=feedback_id,
                            user_id=user_id,
                            emotion_scores=analysis_result.get("emotions", {}),
                            topic_results=analysis_result.get("topics", {}),
                            aspect_results=analysis_result.get("aspects", {}),  # Save ABSA results
                            summary=report.get("summary"),
                            key_insights=report.get("key_insights", []),
                            recommendations=report.get("recommendations", []),
                            analysis_options=options,
                        )

                        db.add(analysis_record)
                        db.commit()
                        db.refresh(analysis_record)

                        logger.info(f"Analysis results saved to database for feedback: {feedback_id}")

                    except Exception as db_error:
                        logger.error(f"Error saving analysis to database: {str(db_error)}", exc_info=True)
                        db.rollback()
                        # Continue even if database save fails

                # Compile final result
                result = {
                    "success": True,
                    "feedback_id": feedback_id,
                    "status": "completed",
                    "emotions": analysis_result.get("emotions", {}),
                    "topics": analysis_result.get("topics", {}),
                    "aspects": analysis_result.get("aspects", {}),  # Include ABSA results
                    "report": report,
                    "statistics": {
                        "total_submitted": len(feedback),
                        "valid_feedback": len(cleaned_texts),
                        "invalid_feedback": ingestion_result["validation"]["invalid_count"],
                    },
                }

                if rag_context:
                    result["rag_context"] = rag_context

                logger.info(f"Feedback processing complete: {feedback_id}")

                return result

        except Exception as e:
            logger.error(f"Error in feedback processing pipeline: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Pipeline execution failed",
                "details": str(e),
            }

    def analyze_existing_feedback(
        self,
        feedback_id: str,
        options: Optional[Dict] = None,
        user_id: Optional[str] = None,
        db=None,
    ) -> Dict:
        """
        Analyze already ingested feedback.

        Args:
            feedback_id: Feedback batch ID
            options: Optional processing options

        Returns:
            Dict: Analysis results
        """
        logger.info(f"Analyzing existing feedback: {feedback_id}")

        options = options or {}

        try:
            # Retrieve feedback
            feedback_data = self.ingestion_agent.get_feedback_by_id(feedback_id)

            if feedback_data["count"] == 0:
                return {
                    "success": False,
                    "error": f"Feedback ID '{feedback_id}' not found",
                }

            texts = feedback_data["documents"]

            # Run analysis
            analysis_result = self.analysis_agent.analyze(
                texts=texts,
                include_topics=options.get("include_topics", True),
                include_emotions=True,
                include_absa=options.get("include_absa", True),  # Include ABSA
            )

            # Generate report
            additional_insights = self.analysis_agent.get_insights(analysis_result)

            report = self.synthesis_agent.synthesize_report(
                feedback_id=feedback_id,
                texts=texts,
                emotion_results=analysis_result.get("emotions", {}),
                topic_results=analysis_result.get("topics", {}),
                additional_insights=additional_insights,
            )

            if options.get("include_summary", True):
                summary = self.synthesis_agent.generate_summary(texts)
                report["summary"] = summary

            # Save analysis results to database if user_id and db provided
            if user_id and db:
                try:
                    from src.db.models import AnalysisResult

                    analysis_record = AnalysisResult(
                        feedback_batch_id=feedback_id,
                        user_id=user_id,
                        emotion_scores=analysis_result.get("emotions", {}),
                        topic_results=analysis_result.get("topics", {}),
                        aspect_results=analysis_result.get("aspects", {}),  # Save ABSA results
                        summary=report.get("summary"),
                        key_insights=report.get("key_insights", []),
                        recommendations=report.get("recommendations", []),
                        analysis_options=options,
                    )

                    db.add(analysis_record)
                    db.commit()
                    db.refresh(analysis_record)

                    logger.info(f"Analysis results saved to database for feedback: {feedback_id}")

                except Exception as db_error:
                    logger.error(f"Error saving analysis to database: {str(db_error)}", exc_info=True)
                    db.rollback()
                    # Continue even if database save fails

            result = {
                "success": True,
                "feedback_id": feedback_id,
                "status": "completed",
                "emotions": analysis_result.get("emotions", {}),
                "topics": analysis_result.get("topics", {}),
                "aspects": analysis_result.get("aspects", {}),  # Include ABSA results
                "report": report,
            }

            logger.info(f"Analysis complete for feedback: {feedback_id}")

            return result

        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "Analysis failed",
                "details": str(e),
            }

    def get_feedback_summary(self, feedback_id: str) -> Dict:
        """
        Get quick summary of feedback batch.

        Args:
            feedback_id: Feedback batch ID

        Returns:
            Dict: Feedback summary
        """
        try:
            feedback_data = self.ingestion_agent.get_feedback_by_id(feedback_id)

            if feedback_data["count"] == 0:
                return {
                    "success": False,
                    "error": f"Feedback ID '{feedback_id}' not found",
                }

            # Get representative samples
            samples = self.retrieval_agent.get_representative_samples(
                feedback_id=feedback_id,
                n_samples=5,
            )

            return {
                "success": True,
                "feedback_id": feedback_id,
                "total_documents": feedback_data["count"],
                "representative_samples": samples.get("samples", []),
            }

        except Exception as e:
            logger.error(f"Error getting feedback summary: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """
    Get global Agent Orchestrator instance.

    Returns:
        AgentOrchestrator: Global orchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
