"""Analysis Agent - Performs sentiment analysis and topic modeling."""

from typing import Dict, List, Optional

from src.services.nlp_processors import (
    get_sentiment_analyzer,
    get_topic_modeler,
)
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class AnalysisAgent:
    """Agent responsible for sentiment analysis and topic modeling."""

    def __init__(self):
        """Initialize Analysis Agent."""
        self.config = get_config()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.topic_modeler = get_topic_modeler()
        logger.info("Analysis Agent initialized")

    def analyze_sentiment(self, texts: List[str]) -> Dict:
        """
        Perform sentiment analysis on texts.

        Args:
            texts: List of text documents

        Returns:
            Dict: Sentiment analysis results with scores and aggregations
        """
        logger.info(f"Analyzing sentiment for {len(texts)} texts")

        with LogExecutionTime(logger, "Sentiment analysis"):
            # Analyze each text
            sentiments = self.sentiment_analyzer.analyze_sentiments(texts)

            # Aggregate results
            aggregated = self.sentiment_analyzer.aggregate_sentiments(sentiments)

            # Add individual sentiment labels
            sentiment_labels = [
                self.sentiment_analyzer.get_sentiment_label(s["compound"])
                for s in sentiments
            ]

            result = {
                "individual_sentiments": sentiments,
                "sentiment_labels": sentiment_labels,
                "aggregated": aggregated,
                "total_analyzed": len(texts),
            }

            logger.info(
                f"Sentiment analysis complete: "
                f"{aggregated.get('sentiment_distribution', {})}"
            )

            return result

    def extract_topics(
        self,
        texts: List[str],
        min_texts: int = 10,
    ) -> Dict:
        """
        Extract topics from texts using BERTopic.

        Args:
            texts: List of text documents
            min_texts: Minimum number of texts required

        Returns:
            Dict: Topic modeling results
        """
        logger.info(f"Extracting topics from {len(texts)} texts")

        with LogExecutionTime(logger, "Topic extraction"):
            # Extract topics
            topics_result = self.topic_modeler.extract_topics(texts, min_texts)

            # Get representative documents for each topic
            if topics_result["topics"]:
                for topic in topics_result["topics"]:
                    topic_id = topic["topic_id"]
                    repr_docs = self.topic_modeler.get_representative_docs(
                        topic_id, n_docs=3
                    )
                    topic["representative_docs"] = repr_docs

            logger.info(
                f"Topic extraction complete: "
                f"{topics_result.get('num_topics', 0)} topics found"
            )

            return topics_result

    def analyze(
        self,
        texts: List[str],
        include_topics: bool = True,
        include_sentiment: bool = True,
    ) -> Dict:
        """
        Perform complete analysis (sentiment + topics).

        Args:
            texts: List of text documents
            include_topics: Whether to include topic modeling
            include_sentiment: Whether to include sentiment analysis

        Returns:
            Dict: Complete analysis results
        """
        logger.info(f"Starting complete analysis of {len(texts)} texts")

        results = {
            "total_documents": len(texts),
            "analysis_performed": [],
        }

        # Sentiment analysis
        if include_sentiment:
            sentiment_results = self.analyze_sentiment(texts)
            results["sentiment"] = sentiment_results["aggregated"]
            results["individual_sentiments"] = sentiment_results["individual_sentiments"]
            results["sentiment_labels"] = sentiment_results["sentiment_labels"]
            results["analysis_performed"].append("sentiment")

        # Topic modeling
        if include_topics and len(texts) >= 10:
            topic_results = self.extract_topics(texts)
            results["topics"] = topic_results
            results["analysis_performed"].append("topics")
        elif include_topics:
            logger.warning(
                f"Skipping topic modeling: insufficient texts ({len(texts)} < 10)"
            )
            results["topics"] = {
                "topics": [],
                "num_topics": 0,
                "message": "Insufficient texts for topic modeling",
            }

        logger.info(
            f"Complete analysis finished: {', '.join(results['analysis_performed'])}"
        )

        return results

    def get_insights(self, analysis_results: Dict) -> List[str]:
        """
        Generate key insights from analysis results.

        Args:
            analysis_results: Results from analyze()

        Returns:
            List[str]: List of key insights
        """
        insights = []

        # Sentiment insights
        if "sentiment" in analysis_results:
            sentiment = analysis_results["sentiment"]
            dist = sentiment.get("sentiment_distribution", {})

            total = sum(dist.values())
            if total > 0:
                pos_pct = (dist.get("positive", 0) / total) * 100
                neg_pct = (dist.get("negative", 0) / total) * 100

                if pos_pct > 60:
                    insights.append(
                        f"Overwhelmingly positive feedback ({pos_pct:.1f}% positive)"
                    )
                elif neg_pct > 60:
                    insights.append(
                        f"Significant negative feedback ({neg_pct:.1f}% negative)"
                    )
                else:
                    insights.append(f"Mixed feedback: {pos_pct:.1f}% positive, {neg_pct:.1f}% negative")

            avg_compound = sentiment.get("average_compound", 0)
            if avg_compound > 0.5:
                insights.append("Overall sentiment is highly positive")
            elif avg_compound < -0.5:
                insights.append("Overall sentiment is highly negative")

        # Topic insights
        if "topics" in analysis_results:
            topics = analysis_results["topics"]
            num_topics = topics.get("num_topics", 0)

            if num_topics > 0:
                insights.append(f"Identified {num_topics} distinct themes in feedback")

                # Highlight top topic
                topic_list = topics.get("topics", [])
                if topic_list:
                    top_topic = max(topic_list, key=lambda t: t["count"])
                    keywords = ", ".join(top_topic["keywords"][:3])
                    insights.append(
                        f"Most discussed theme: {keywords} ({top_topic['count']} mentions)"
                    )

        return insights


# Global agent instance
_analysis_agent: Optional[AnalysisAgent] = None


def get_analysis_agent() -> AnalysisAgent:
    """
    Get global Analysis Agent instance.

    Returns:
        AnalysisAgent: Global agent instance
    """
    global _analysis_agent
    if _analysis_agent is None:
        _analysis_agent = AnalysisAgent()
    return _analysis_agent
