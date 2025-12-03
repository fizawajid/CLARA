"""NLP processing services: sentiment analysis, topic modeling, and summarization."""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import spacy
from bertopic import BERTopic
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """VADER-based sentiment analysis service."""

    def __init__(self):
        """Initialize VADER sentiment analyzer."""
        logger.info("Initializing VADER sentiment analyzer")
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER sentiment analyzer ready")

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text.

        Args:
            text: Input text to analyze

        Returns:
            Dict: Sentiment scores (negative, neutral, positive, compound)
        """
        if not text or not text.strip():
            return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

        try:
            scores = self.analyzer.polarity_scores(text)
            return scores
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

    def analyze_sentiments(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment of multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List[Dict]: List of sentiment scores
        """
        logger.info(f"Analyzing sentiment for {len(texts)} texts")
        results = [self.analyze_sentiment(text) for text in texts]
        logger.info("Sentiment analysis complete")
        return results

    def get_sentiment_label(self, compound_score: float) -> str:
        """
        Convert compound score to sentiment label.

        Args:
            compound_score: VADER compound score

        Returns:
            str: Sentiment label (positive, negative, neutral)
        """
        config = get_config()
        threshold = config.nlp.sentiment_threshold

        if compound_score >= threshold:
            return "positive"
        elif compound_score <= -threshold:
            return "negative"
        else:
            return "neutral"

    def aggregate_sentiments(self, sentiments: List[Dict[str, float]]) -> Dict:
        """
        Aggregate sentiment scores across multiple texts.

        Args:
            sentiments: List of sentiment score dicts

        Returns:
            Dict: Aggregated statistics
        """
        if not sentiments:
            return {}

        df = pd.DataFrame(sentiments)

        return {
            "average_compound": float(df["compound"].mean()),
            "average_positive": float(df["pos"].mean()),
            "average_negative": float(df["neg"].mean()),
            "average_neutral": float(df["neu"].mean()),
            "sentiment_distribution": {
                "positive": int((df["compound"] >= 0.05).sum()),
                "neutral": int(((df["compound"] > -0.05) & (df["compound"] < 0.05)).sum()),
                "negative": int((df["compound"] <= -0.05).sum()),
            },
        }


class TopicModeler:
    """BERTopic-based topic modeling service."""

    def __init__(self, embedding_model: Optional[str] = None):
        """
        Initialize BERTopic topic modeler.

        Args:
            embedding_model: Name of embedding model to use
        """
        config = get_config()
        self.embedding_model = embedding_model or config.models.embedding_model
        self.min_topic_size = config.nlp.min_topic_size
        self.max_topics = config.nlp.max_topics

        logger.info(f"Initializing BERTopic with model: {self.embedding_model}")

        # Initialize BERTopic with custom settings
        self.model = BERTopic(
            embedding_model=self.embedding_model,
            min_topic_size=self.min_topic_size,
            nr_topics=self.max_topics,
            verbose=False,
        )

        self.is_fitted = False
        logger.info("BERTopic topic modeler ready")

    def extract_topics(
        self,
        texts: List[str],
        min_texts: int = 10,
    ) -> Dict:
        """
        Extract topics from texts using BERTopic.

        Args:
            texts: List of input texts
            min_texts: Minimum number of texts required

        Returns:
            Dict: Topics with keywords and document assignments
        """
        if len(texts) < min_texts:
            logger.warning(f"Not enough texts for topic modeling (need {min_texts}, got {len(texts)})")
            return {
                "topics": [],
                "topic_assignments": [-1] * len(texts),
                "topic_info": [],
            }

        try:
            logger.info(f"Extracting topics from {len(texts)} texts")

            # Fit the model and get topics
            topics, probabilities = self.model.fit_transform(texts)
            self.is_fitted = True

            # Get topic information
            topic_info = self.model.get_topic_info()

            # Extract top words for each topic
            topic_list = []
            for topic_id in topic_info["Topic"].values:
                if topic_id == -1:  # Skip outlier topic
                    continue

                topic_words = self.model.get_topic(topic_id)
                if topic_words:
                    topic_list.append({
                        "topic_id": int(topic_id),
                        "keywords": [word for word, _ in topic_words[:10]],
                        "scores": [float(score) for _, score in topic_words[:10]],
                        "count": int(topic_info[topic_info["Topic"] == topic_id]["Count"].values[0]),
                    })

            logger.info(f"Extracted {len(topic_list)} topics")

            return {
                "topics": topic_list,
                "topic_assignments": [int(t) for t in topics],
                "num_topics": len(topic_list),
                "outliers": int((np.array(topics) == -1).sum()),
            }

        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return {
                "topics": [],
                "topic_assignments": [-1] * len(texts),
                "num_topics": 0,
            }

    def get_representative_docs(
        self,
        topic_id: int,
        n_docs: int = 3,
    ) -> List[str]:
        """
        Get representative documents for a topic.

        Args:
            topic_id: Topic ID
            n_docs: Number of documents to return

        Returns:
            List[str]: Representative documents
        """
        if not self.is_fitted:
            logger.warning("Model not fitted yet")
            return []

        try:
            repr_docs = self.model.get_representative_docs(topic_id)
            return repr_docs[:n_docs] if repr_docs else []
        except Exception as e:
            logger.error(f"Error getting representative docs: {str(e)}")
            return []


class TextSummarizer:
    """spaCy + TextRank based text summarization service."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize text summarizer.

        Args:
            model_name: spaCy model name
        """
        config = get_config()
        self.model_name = model_name or config.models.spacy_model
        self.summary_ratio = config.nlp.summary_ratio

        logger.info(f"Loading spaCy model: {self.model_name}")
        try:
            self.nlp = spacy.load(self.model_name)
            # Add TextRank to the pipeline
            self.nlp.add_pipe("textrank")
            logger.info("Text summarizer ready with TextRank")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {str(e)}")
            raise

    def summarize(
        self,
        text: str,
        ratio: Optional[float] = None,
        max_sentences: int = 5,
    ) -> str:
        """
        Summarize a single text using TextRank.

        Args:
            text: Input text to summarize
            ratio: Ratio of sentences to keep (0-1)
            max_sentences: Maximum number of sentences in summary

        Returns:
            str: Summarized text
        """
        if not text or not text.strip():
            return ""

        ratio = ratio or self.summary_ratio

        try:
            doc = self.nlp(text)

            # Get sentences with their TextRank scores
            sentences = []
            for sent in doc._.textrank.summary(limit_phrases=15, limit_sentences=max_sentences):
                sentences.append(str(sent))

            summary = " ".join(sentences)
            return summary if summary else text[:500]  # Fallback to first 500 chars

        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            # Fallback: return first few sentences
            sentences = text.split(". ")
            return ". ".join(sentences[:max_sentences]) + "."

    def summarize_multiple(
        self,
        texts: List[str],
        ratio: Optional[float] = None,
    ) -> List[str]:
        """
        Summarize multiple texts.

        Args:
            texts: List of input texts
            ratio: Ratio of sentences to keep

        Returns:
            List[str]: List of summaries
        """
        logger.info(f"Summarizing {len(texts)} texts")
        summaries = [self.summarize(text, ratio) for text in texts]
        logger.info("Summarization complete")
        return summaries

    def extract_key_phrases(self, text: str, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Extract key phrases from text.

        Args:
            text: Input text
            limit: Maximum number of phrases

        Returns:
            List[Tuple]: List of (phrase, score) tuples
        """
        try:
            doc = self.nlp(text)
            phrases = []

            for phrase in doc._.phrases[:limit]:
                phrases.append((phrase.text, phrase.rank))

            return phrases

        except Exception as e:
            logger.error(f"Error extracting key phrases: {str(e)}")
            return []


# Global NLP service instances
_sentiment_analyzer: Optional[SentimentAnalyzer] = None
_topic_modeler: Optional[TopicModeler] = None
_text_summarizer: Optional[TextSummarizer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get global sentiment analyzer instance."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer


def get_topic_modeler() -> TopicModeler:
    """Get global topic modeler instance."""
    global _topic_modeler
    if _topic_modeler is None:
        _topic_modeler = TopicModeler()
    return _topic_modeler


def get_text_summarizer() -> TextSummarizer:
    """Get global text summarizer instance."""
    global _text_summarizer
    if _text_summarizer is None:
        _text_summarizer = TextSummarizer()
    return _text_summarizer
