"""Synthesis Agent - Generates comprehensive insights and reports."""

from typing import Dict, List, Optional

from src.services.nlp_processors import get_text_summarizer
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class SynthesisAgent:
    """Agent responsible for synthesizing analysis results into reports."""

    def __init__(self):
        """Initialize Synthesis Agent."""
        self.config = get_config()
        self.text_summarizer = get_text_summarizer()
        logger.info("Synthesis Agent initialized")

    def generate_summary(
        self,
        texts: List[str],
        max_length: int = 500,
    ) -> str:
        """
        Generate overall summary from multiple texts.

        Args:
            texts: List of text documents
            max_length: Maximum summary length

        Returns:
            str: Generated summary
        """
        logger.info(f"Generating summary from {len(texts)} texts")

        if not texts:
            return "No feedback available for summarization."

        with LogExecutionTime(logger, "Summary generation"):
            # Combine texts for summarization
            combined_text = " ".join(texts[:50])  # Limit to first 50 for efficiency

            # Generate summary
            summary = self.text_summarizer.summarize(
                text=combined_text,
                max_sentences=5,
            )

            # Trim to max length
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."

            logger.info(f"Generated summary of length {len(summary)}")

            return summary

    def synthesize_sentiment_insights(self, sentiment_results: Dict) -> List[str]:
        """
        Generate insights from sentiment analysis results.

        Args:
            sentiment_results: Sentiment analysis results

        Returns:
            List[str]: List of sentiment insights
        """
        insights = []

        if not sentiment_results:
            return insights

        # Overall sentiment
        avg_compound = sentiment_results.get("average_compound", 0)
        if avg_compound > 0.5:
            insights.append("Overwhelmingly positive customer sentiment detected")
        elif avg_compound > 0.1:
            insights.append("Generally positive customer sentiment")
        elif avg_compound < -0.5:
            insights.append("Significant negative sentiment requiring attention")
        elif avg_compound < -0.1:
            insights.append("Moderate negative sentiment detected")
        else:
            insights.append("Neutral sentiment overall")

        # Distribution analysis
        dist = sentiment_results.get("sentiment_distribution", {})
        total = sum(dist.values())

        if total > 0:
            pos_pct = (dist.get("positive", 0) / total) * 100
            neg_pct = (dist.get("negative", 0) / total) * 100
            neu_pct = (dist.get("neutral", 0) / total) * 100

            insights.append(
                f"Sentiment breakdown: {pos_pct:.1f}% positive, "
                f"{neu_pct:.1f}% neutral, {neg_pct:.1f}% negative"
            )

            # Highlight concerns
            if neg_pct > 30:
                insights.append(
                    f"⚠️ High proportion of negative feedback ({neg_pct:.1f}%) needs investigation"
                )

            # Highlight strengths
            if pos_pct > 70:
                insights.append(
                    f"✓ Strong positive reception ({pos_pct:.1f}%)"
                )

        return insights

    def synthesize_topic_insights(self, topic_results: Dict) -> List[str]:
        """
        Generate insights from topic modeling results.

        Args:
            topic_results: Topic modeling results

        Returns:
            List[str]: List of topic insights
        """
        insights = []

        if not topic_results:
            return insights

        num_topics = topic_results.get("num_topics", 0)
        topics = topic_results.get("topics", [])

        if num_topics == 0:
            insights.append("No distinct topics identified in feedback")
            return insights

        insights.append(f"Identified {num_topics} distinct discussion themes")

        # Analyze top topics
        if topics:
            # Sort by document count
            sorted_topics = sorted(topics, key=lambda t: t["count"], reverse=True)

            # Top 3 topics
            for idx, topic in enumerate(sorted_topics[:3], 1):
                keywords = ", ".join(topic["keywords"][:3])
                count = topic["count"]
                insights.append(
                    f"Theme #{idx}: {keywords} ({count} mentions)"
                )

            # Topic distribution analysis
            total_docs = sum(t["count"] for t in topics)
            top_topic_count = sorted_topics[0]["count"]
            top_topic_pct = (top_topic_count / total_docs) * 100 if total_docs > 0 else 0

            if top_topic_pct > 40:
                insights.append(
                    f"Dominant theme accounts for {top_topic_pct:.1f}% of feedback"
                )

        # Outliers
        outliers = topic_results.get("outliers", 0)
        if outliers > 0:
            insights.append(
                f"{outliers} feedback entries don't fit main themes (unique concerns)"
            )

        return insights

    def generate_recommendations(
        self,
        sentiment_results: Dict,
        topic_results: Dict,
    ) -> List[str]:
        """
        Generate actionable recommendations based on analysis.

        Args:
            sentiment_results: Sentiment analysis results
            topic_results: Topic modeling results

        Returns:
            List[str]: List of recommendations
        """
        recommendations = []

        # Sentiment-based recommendations
        if sentiment_results:
            avg_compound = sentiment_results.get("average_compound", 0)
            dist = sentiment_results.get("sentiment_distribution", {})
            total = sum(dist.values())
            neg_pct = (dist.get("negative", 0) / total) * 100 if total > 0 else 0

            if neg_pct > 25:
                recommendations.append(
                    "Priority: Address negative feedback themes to improve satisfaction"
                )

            if avg_compound < 0:
                recommendations.append(
                    "Conduct deeper analysis on pain points mentioned in negative feedback"
                )

        # Topic-based recommendations
        if topic_results:
            topics = topic_results.get("topics", [])
            if topics:
                sorted_topics = sorted(topics, key=lambda t: t["count"], reverse=True)

                # Recommend focusing on top themes
                if len(sorted_topics) >= 1:
                    top_keywords = ", ".join(sorted_topics[0]["keywords"][:3])
                    recommendations.append(
                        f"Focus on most discussed theme: {top_keywords}"
                    )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Monitor feedback trends over time for emerging patterns"
            )

        return recommendations

    def synthesize_report(
        self,
        feedback_id: str,
        texts: List[str],
        sentiment_results: Dict,
        topic_results: Dict,
        additional_insights: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate comprehensive analysis report.

        Args:
            feedback_id: Feedback batch ID
            texts: Original feedback texts
            sentiment_results: Sentiment analysis results
            topic_results: Topic modeling results
            additional_insights: Optional additional insights

        Returns:
            Dict: Comprehensive report
        """
        logger.info("Synthesizing comprehensive report")

        with LogExecutionTime(logger, "Report synthesis"):
            # Generate summary
            summary = self.generate_summary(texts)

            # Generate insights
            sentiment_insights = self.synthesize_sentiment_insights(sentiment_results)
            topic_insights = self.synthesize_topic_insights(topic_results)

            # Combine all insights
            all_insights = sentiment_insights + topic_insights
            if additional_insights:
                all_insights.extend(additional_insights)

            # Generate recommendations
            recommendations = self.generate_recommendations(
                sentiment_results, topic_results
            )

            report = {
                "feedback_id": feedback_id,
                "summary": summary,
                "key_insights": all_insights,
                "recommendations": recommendations,
                "statistics": {
                    "total_feedback": len(texts),
                    "topics_identified": topic_results.get("num_topics", 0),
                    "average_sentiment": sentiment_results.get("average_compound", 0),
                },
            }

            logger.info("Report synthesis complete")

            return report

    def create_executive_summary(self, report: Dict) -> str:
        """
        Create executive summary from full report.

        Args:
            report: Full analysis report

        Returns:
            str: Executive summary
        """
        stats = report.get("statistics", {})
        insights = report.get("key_insights", [])[:3]  # Top 3 insights

        exec_summary = f"""
EXECUTIVE SUMMARY
=================

Feedback Analysis: {stats.get('total_feedback', 0)} responses analyzed

Key Findings:
{chr(10).join(f'• {insight}' for insight in insights)}

Overall Sentiment: {'Positive' if stats.get('average_sentiment', 0) > 0 else 'Negative' if stats.get('average_sentiment', 0) < 0 else 'Neutral'}

Topics Identified: {stats.get('topics_identified', 0)} major themes

For detailed analysis, see full report.
"""
        return exec_summary.strip()


# Global agent instance
_synthesis_agent: Optional[SynthesisAgent] = None


def get_synthesis_agent() -> SynthesisAgent:
    """
    Get global Synthesis Agent instance.

    Returns:
        SynthesisAgent: Global agent instance
    """
    global _synthesis_agent
    if _synthesis_agent is None:
        _synthesis_agent = SynthesisAgent()
    return _synthesis_agent
