"""NLP processing services: emotion analysis, topic modeling, and summarization."""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import spacy
import pytextrank
from bertopic import BERTopic
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EmotionAnalyzer:
    """Hybrid emotion analysis service combining sentiment analysis with emotion detection."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize hybrid emotion analyzer with sentiment model."""
        config = get_config()
        # Use a sentiment model that works better for reviews
        self.sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.emotion_categories = config.models.emotion_categories

        logger.info(f"Initializing emotion analyzer with sentiment model: {self.sentiment_model_name}")

        try:
            # Load sentiment analysis model (works better for reviews)
            self.tokenizer = AutoTokenizer.from_pretrained(self.sentiment_model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.sentiment_model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model.eval()

            # Sentiment labels: negative, neutral, positive
            self.sentiment_labels = ["negative", "neutral", "positive"]

            logger.info(f"Emotion analyzer ready on device: {self.device}")
        except Exception as e:
            logger.error(f"Error initializing emotion analyzer: {str(e)}")
            raise

    def analyze_emotion(self, text: str) -> Dict[str, float]:
        """
        Analyze emotions using hybrid sentiment + keyword approach.

        Args:
            text: Input text to analyze

        Returns:
            Dict: Emotion scores for 6 emotions + dominant emotion
        """
        if not text or not text.strip():
            # Return neutral when empty
            return {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "neutral": 1.0,
                "dominant_emotion": "neutral"
            }

        try:
            # Step 1: Get sentiment scores (negative, neutral, positive)
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                sentiment_probs = F.softmax(logits, dim=-1)[0].cpu()

            negative_score = float(sentiment_probs[0])
            neutral_score = float(sentiment_probs[1])
            positive_score = float(sentiment_probs[2])

            # Step 2: Map sentiment to emotions using keyword analysis
            text_lower = text.lower()

            # Initialize emotion scores
            emotion_scores = {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "neutral": neutral_score
            }

            # Define keyword dictionaries
            joy_keywords = ["excellent", "great", "love", "perfect", "amazing", "wonderful",
                           "fantastic", "happy", "best", "quality", "solid", "good", "like",
                           "sturdy", "well-made", "rock-solid", "quick", "painless"]
            joy_count = sum(1 for word in joy_keywords if word in text_lower)

            sadness_keywords = ["disappointed", "unfortunate", "sad", "uncomfortable",
                               "regret", "poor", "falls short", "lacking", "miss",
                               "prevent", "defeats", "slightly"]
            sadness_count = sum(1 for word in sadness_keywords if word in text_lower)

            anger_keywords = ["annoying", "frustrating", "terrible", "awful", "hate",
                             "ridiculous", "unacceptable", "worst"]
            anger_count = sum(1 for word in anger_keywords if word in text_lower)

            fear_keywords = ["worried", "concerned", "afraid", "anxious", "nervous"]
            fear_count = sum(1 for word in fear_keywords if word in text_lower)

            surprise_keywords = ["surprising", "unexpected", "amazed", "shocked", "wow"]
            surprise_count = sum(1 for word in surprise_keywords if word in text_lower)

            # Determine sentiment type
            max_sentiment = max(positive_score, negative_score, neutral_score)

            # Mixed sentiment: positive and negative both significant
            is_mixed = (positive_score > 0.2 and negative_score > 0.2) or \
                      (positive_score > 0.3 and negative_score > 0.15) or \
                      (positive_score > 0.15 and negative_score > 0.3)

            if is_mixed:
                # Mixed review: distribute across emotions based on keywords and scores
                base_joy = positive_score * 0.5
                joy_boost = min(0.5, joy_count * 0.08)
                emotion_scores["joy"] = base_joy + joy_boost * positive_score

                base_sadness = negative_score * 0.5
                sadness_boost = min(0.5, sadness_count * 0.08)
                emotion_scores["sadness"] = base_sadness + sadness_boost * negative_score

                # Add some anger if negative keywords present
                if anger_count > 0:
                    emotion_scores["anger"] = negative_score * (0.25 + min(0.25, anger_count * 0.1))
                else:
                    emotion_scores["anger"] = negative_score * 0.1

                # Keep some neutral
                emotion_scores["neutral"] = neutral_score * 0.4

                if surprise_count > 0:
                    emotion_scores["surprise"] = 0.1

            elif positive_score > 0.4:
                # Clear positive sentiment
                if surprise_count > 0:
                    emotion_scores["surprise"] = positive_score * 0.6
                    emotion_scores["joy"] = positive_score * 0.4
                else:
                    base_joy = positive_score * 0.7
                    joy_boost = min(0.3, joy_count * 0.05)
                    emotion_scores["joy"] = base_joy + joy_boost

            elif negative_score > 0.4:
                # Clear negative sentiment
                if anger_count > sadness_count and anger_count > 0:
                    emotion_scores["anger"] = negative_score * 0.7
                    emotion_scores["sadness"] = negative_score * 0.3
                elif fear_count > 0:
                    emotion_scores["fear"] = negative_score * 0.6
                    emotion_scores["sadness"] = negative_score * 0.4
                else:
                    # Default to sadness for negative reviews
                    base_sadness = negative_score * 0.7
                    sadness_boost = min(0.3, sadness_count * 0.08)
                    emotion_scores["sadness"] = base_sadness + sadness_boost
                    emotion_scores["anger"] = negative_score * 0.15

            else:
                # Truly neutral or unclear - still try to extract emotions from keywords
                if joy_count > 0:
                    emotion_scores["joy"] = min(0.4, joy_count * 0.1)
                if sadness_count > 0:
                    emotion_scores["sadness"] = min(0.4, sadness_count * 0.1)
                if anger_count > 0:
                    emotion_scores["anger"] = min(0.3, anger_count * 0.1)

            # Normalize scores to sum to 1.0
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v / total for k, v in emotion_scores.items()}

            # Get dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            emotion_scores["dominant_emotion"] = dominant_emotion

            return emotion_scores

        except Exception as e:
            logger.error(f"Error analyzing emotion: {str(e)}")
            return {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "neutral": 1.0,
                "dominant_emotion": "neutral"
            }

    def analyze_emotions(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze emotions of multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List[Dict]: List of emotion scores
        """
        logger.info(f"Analyzing emotions for {len(texts)} texts")
        results = [self.analyze_emotion(text) for text in texts]
        logger.info("Emotion analysis complete")
        return results

    def get_dominant_emotion(self, emotion_scores: Dict[str, float]) -> str:
        """
        Get the dominant emotion from scores.

        Args:
            emotion_scores: Dict of emotion scores

        Returns:
            str: Dominant emotion label
        """
        # Filter out non-emotion keys
        emotions_only = {k: v for k, v in emotion_scores.items() if k != "dominant_emotion"}
        return max(emotions_only.items(), key=lambda x: x[1])[0]

    def aggregate_emotions(self, emotions: List[Dict[str, float]]) -> Dict:
        """
        Aggregate emotion scores across multiple texts.

        Args:
            emotions: List of emotion score dicts

        Returns:
            Dict: Aggregated statistics
        """
        if not emotions:
            return {}

        # Remove dominant_emotion key for aggregation
        emotions_clean = []
        for e in emotions:
            emotions_clean.append({k: v for k, v in e.items() if k != "dominant_emotion"})

        df = pd.DataFrame(emotions_clean)

        # Calculate average scores for each emotion
        average_scores = {
            emotion: float(df[emotion].mean())
            for emotion in self.emotion_categories
        }

        # Calculate emotion distribution (count of dominant emotion)
        emotion_distribution = {}
        for emotion in self.emotion_categories:
            count = sum(1 for e in emotions if e.get("dominant_emotion") == emotion)
            emotion_distribution[emotion] = int(count)

        # Get overall dominant emotion
        dominant_emotion = max(average_scores.items(), key=lambda x: x[1])[0]

        # Calculate emotion diversity (Shannon entropy)
        emotion_diversity = self._calculate_entropy(list(average_scores.values()))

        return {
            "average_scores": average_scores,
            "emotion_distribution": emotion_distribution,
            "dominant_emotion": dominant_emotion,
            "emotion_diversity": float(emotion_diversity)
        }

    def _calculate_entropy(self, probabilities: List[float]) -> float:
        """
        Calculate Shannon entropy for emotion diversity.

        Args:
            probabilities: List of emotion probabilities

        Returns:
            float: Entropy value (0-1 normalized)
        """
        try:
            # Normalize probabilities
            total = sum(probabilities)
            if total == 0:
                return 0.0

            probs = [p / total for p in probabilities]

            # Calculate entropy
            entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)

            # Normalize by max entropy (log of number of emotions)
            max_entropy = np.log(len(probabilities))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

            return float(normalized_entropy)
        except Exception as e:
            logger.error(f"Error calculating entropy: {str(e)}")
            return 0.0


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

        # Initialize CountVectorizer with stopwords filtering
        from sklearn.feature_extraction.text import CountVectorizer
        from umap import UMAP
        from hdbscan import HDBSCAN

        self.vectorizer_model = CountVectorizer(
            stop_words='english',  # Remove English stopwords
            min_df=1,  # Minimum document frequency
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=1000  # Limit vocabulary size
        )

        # UMAP for dimensionality reduction (optimized for small datasets)
        self.umap_model = UMAP(
            n_neighbors=3,  # Lower for small datasets (min 2, default 15)
            n_components=5,  # Dimensions to reduce to
            min_dist=0.0,  # Tighter clusters
            metric='cosine',
            random_state=42
        )

        # HDBSCAN for clustering (more lenient for small datasets)
        self.hdbscan_model = HDBSCAN(
            min_cluster_size=2,  # Same as min_topic_size
            min_samples=1,  # More lenient (allows more clusters)
            metric='euclidean',
            cluster_selection_method='eom',  # Excess of mass
            prediction_data=True
        )

        # Initialize BERTopic with custom settings
        self.model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            vectorizer_model=self.vectorizer_model,
            nr_topics=self.max_topics,
            verbose=False,
        )

        self.is_fitted = False
        logger.info("BERTopic topic modeler ready with stopwords filtering")

    def extract_topics(
        self,
        texts: List[str],
        min_texts: int = 3,  # Lowered from 10 to work with small datasets
    ) -> Dict:
        """
        Extract topics from texts using BERTopic.

        Args:
            texts: List of input texts
            min_texts: Minimum number of texts required (default 3)

        Returns:
            Dict: Topics with keywords and document assignments
        """
        if len(texts) < min_texts:
            logger.warning(f"Not enough texts for topic modeling (need {min_texts}, got {len(texts)})")
            return {
                "topics": [],
                "topic_assignments": [-1] * len(texts),
                "topic_info": [],
                "num_topics": 0,
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
                    # Get representative documents for this topic
                    topic_docs_indices = [i for i, t in enumerate(topics) if t == topic_id]
                    representative_docs = [texts[i] for i in topic_docs_indices[:3]]  # Get first 3 docs

                    topic_list.append({
                        "topic_id": int(topic_id),
                        "keywords": [word for word, _ in topic_words[:10]],
                        "scores": [float(score) for _, score in topic_words[:10]],
                        "count": int(topic_info[topic_info["Topic"] == topic_id]["Count"].values[0]),
                        "representative_docs": representative_docs,  # Added representative docs
                    })

            logger.info(f"Extracted {len(topic_list)} topics with representative documents")

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
        config = get_config()
        self.model_name = model_name or config.models.spacy_model
        self.summary_ratio = config.nlp.summary_ratio

        logger.info(f"Loading spaCy model: {self.model_name}")
        try:
            self.nlp = spacy.load(self.model_name)
            self.nlp.add_pipe("textrank")  # <- correct
            logger.info("Text summarizer ready with PyTextRank")
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
_emotion_analyzer: Optional[EmotionAnalyzer] = None
_topic_modeler: Optional[TopicModeler] = None
_text_summarizer: Optional[TextSummarizer] = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    """Get global emotion analyzer instance."""
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer


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
