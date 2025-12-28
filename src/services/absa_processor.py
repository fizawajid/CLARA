"""Aspect-Based Sentiment Analysis (ABSA) processor service."""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import re
import spacy
from transformers import pipeline

from src.utils.config import get_config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AspectBasedSentimentAnalyzer:
    """
    Hybrid ABSA system combining:
    1. Predefined aspect categories (for consistency)
    2. Automatic aspect discovery (for flexibility)
    3. Transformer-based sentiment classification (for accuracy)
    """

    def __init__(self):
        """Initialize ABSA analyzer with models and aspect taxonomy."""

        config = get_config()

        # Load aspect categories from config
        self.aspect_categories = config.absa.aspect_categories if hasattr(config, 'absa') else {
            "product": ["quality", "product", "item", "material", "build", "features"],
            "price": ["price", "cost", "value", "expensive", "cheap", "affordable"],
            "delivery": ["delivery", "shipping", "logistics", "arrival", "package"],
            "service": ["service", "support", "customer service", "help", "assistance"],
            "usability": ["easy", "difficult", "simple", "complex", "user-friendly", "intuitive"],
            "performance": ["fast", "slow", "performance", "speed", "efficient", "responsive"],
            "design": ["design", "look", "appearance", "aesthetic", "style", "interface"]
        }

        # Configuration parameters
        self.context_window = 100  # Characters around aspect mention (increased for better context)
        self.confidence_threshold = 0.5  # Lowered threshold for better sensitivity
        self.min_aspect_mentions = 1

        logger.info("Initializing ABSA analyzer...")

        try:
            # Load spaCy for noun phrase extraction
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✓ spaCy model loaded")

            # Load sentiment classifier (5-star rating model for granularity)
            self.sentiment_classifier = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=-1  # CPU
            )
            logger.info("✓ Sentiment classifier loaded")

            logger.info("ABSA analyzer ready")

        except Exception as e:
            logger.error(f"Error initializing ABSA analyzer: {str(e)}")
            raise

    def extract_aspects(self, texts: List[str]) -> List[Dict]:
        """
        Extract aspects from feedback texts using hybrid approach.

        Args:
            texts: List of feedback texts

        Returns:
            List of dicts with aspect information per text
        """
        logger.info(f"Extracting aspects from {len(texts)} texts")

        all_aspects = []

        for text in texts:
            # Stage 1: Match predefined aspects
            predefined = self._match_predefined_aspects(text)

            # Stage 2: Discover new aspects (noun phrases)
            discovered = self._discover_new_aspects(text)

            # Stage 3: Consolidate and deduplicate
            consolidated = self._consolidate_aspects(predefined, discovered, text)

            all_aspects.append({
                "text": text,
                "aspects": consolidated
            })

        logger.info(f"Aspect extraction complete")
        return all_aspects

    def _match_predefined_aspects(self, text: str) -> List[Dict]:
        """
        Match predefined aspect keywords in text.

        Args:
            text: Input text

        Returns:
            List of found aspects with context
        """
        text_lower = text.lower()
        found_aspects = []

        for category, keywords in self.aspect_categories.items():
            for keyword in keywords:
                # Use word boundary matching to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    # Find position for context extraction
                    match = re.search(pattern, text_lower)
                    if match:
                        position = match.start()
                        context = self._extract_context_window(text, position, self.context_window)

                        found_aspects.append({
                            "aspect": category,
                            "term": keyword,
                            "context": context,
                            "position": position,
                            "source": "predefined"
                        })
                        break  # One match per category

        return found_aspects

    def _discover_new_aspects(self, text: str) -> List[Dict]:
        """
        Discover new aspect candidates using noun phrase extraction.

        Args:
            text: Input text

        Returns:
            List of discovered aspect candidates
        """
        try:
            doc = self.nlp(text)
            discovered = []

            # Extract noun chunks as potential aspects
            for chunk in doc.noun_chunks:
                # Filter: must be 1-3 words, not too generic
                if 1 <= len(chunk.text.split()) <= 3:
                    # Skip very generic words and pronouns
                    generic_words = {
                        'it', 'this', 'that', 'these', 'those', 'thing', 'something',
                        'i', 'you', 'we', 'they', 'he', 'she', 'which', 'who', 'what',
                        'the issue', 'the problem', 'the thing', 'everything', 'anything'
                    }
                    chunk_lower = chunk.text.lower().strip()

                    # Skip if generic or too short
                    if chunk_lower not in generic_words and len(chunk_lower) > 1:
                        # Skip single letters and pure pronouns
                        if not (len(chunk_lower) == 1 or chunk.root.pos_ == 'PRON'):
                            discovered.append({
                                "aspect": chunk_lower,
                                "term": chunk.text,
                                "context": self._extract_context_window(text, chunk.start_char, self.context_window),
                                "position": chunk.start_char,
                                "source": "discovered"
                            })

            return discovered

        except Exception as e:
            logger.error(f"Error discovering aspects: {str(e)}")
            return []

    def _consolidate_aspects(self, predefined: List[Dict], discovered: List[Dict], text: str) -> List[Dict]:
        """
        Consolidate predefined and discovered aspects, removing duplicates.

        Args:
            predefined: List of predefined aspects
            discovered: List of discovered aspects
            text: Original text

        Returns:
            Consolidated list of unique aspects
        """
        # Priority: predefined aspects first
        consolidated = {}

        # Add predefined aspects
        for aspect in predefined:
            key = aspect["aspect"]
            if key not in consolidated:
                consolidated[key] = aspect

        # Add discovered aspects if they don't overlap with predefined
        for aspect in discovered:
            # Check if discovered aspect is already covered by predefined
            is_duplicate = False
            aspect_term = aspect["term"].lower()

            for pred_category, pred_keywords in self.aspect_categories.items():
                if any(keyword in aspect_term for keyword in pred_keywords):
                    is_duplicate = True
                    break

            if not is_duplicate:
                # Use the discovered term as the aspect name
                key = aspect["aspect"]
                if key not in consolidated:
                    consolidated[key] = aspect

        return list(consolidated.values())

    def _extract_context_window(self, text: str, position: int, window_size: int) -> str:
        """
        Extract context window around aspect mention.

        Args:
            text: Full text
            position: Position of aspect mention
            window_size: Window size in characters

        Returns:
            Context string
        """
        start = max(0, position - window_size)
        end = min(len(text), position + window_size)
        return text[start:end].strip()

    def analyze_aspect_sentiment(self, text: str, aspect: str, context: str) -> Dict:
        """
        Analyze sentiment toward specific aspect using context window.

        Args:
            text: Full feedback text
            aspect: Aspect name
            context: Context window around aspect

        Returns:
            Dict with sentiment analysis results
        """
        try:
            # Classify sentiment on context (not full text)
            result = self.sentiment_classifier(context)[0]

            # Map 5-star labels to positive/neutral/negative
            label = result['label']
            score = result['score']

            if '5 star' in label or '4 star' in label:
                sentiment = 'positive'
            elif '3 star' in label:
                sentiment = 'neutral'
            else:  # 1 or 2 stars
                sentiment = 'negative'

            return {
                "aspect": aspect,
                "sentiment": sentiment,
                "confidence": score,
                "context": context,
                "raw_label": label
            }

        except Exception as e:
            logger.error(f"Error analyzing aspect sentiment: {str(e)}")
            return {
                "aspect": aspect,
                "sentiment": "neutral",
                "confidence": 0.5,
                "context": context,
                "error": str(e)
            }

    def analyze_batch(self, texts: List[str]) -> Dict:
        """
        Complete ABSA analysis on batch of texts.

        Args:
            texts: List of feedback texts

        Returns:
            Dict with complete ABSA results including aggregations
        """
        logger.info(f"Starting ABSA batch analysis on {len(texts)} texts")

        # Extract aspects from all texts
        aspect_extractions = self.extract_aspects(texts)

        # Analyze sentiment for each aspect
        aspect_results = []

        for extraction in aspect_extractions:
            text = extraction["text"]
            aspects = extraction["aspects"]

            for aspect_data in aspects:
                sentiment = self.analyze_aspect_sentiment(
                    text=text,
                    aspect=aspect_data["aspect"],
                    context=aspect_data["context"]
                )

                # Add position and source information
                sentiment["term"] = aspect_data["term"]
                sentiment["position"] = aspect_data["position"]
                sentiment["source"] = aspect_data["source"]
                sentiment["original_text"] = text

                aspect_results.append(sentiment)

        # Aggregate results
        aggregated = self.aggregate_aspect_sentiments(aspect_results)

        logger.info(f"ABSA analysis complete: {len(aggregated['aspects'])} aspects found")

        return aggregated

    def aggregate_aspect_sentiments(self, aspect_results: List[Dict]) -> Dict:
        """
        Aggregate aspect sentiments across all feedback.

        Args:
            aspect_results: List of aspect sentiment results

        Returns:
            Dict with aggregated statistics and recommendations
        """
        if not aspect_results:
            return {
                "aspects": {},
                "summary": {
                    "top_positive_aspects": [],
                    "top_negative_aspects": [],
                    "priority_recommendations": []
                },
                "total_aspects": 0,
                "total_mentions": 0
            }

        # Aggregate by aspect
        aspect_stats = defaultdict(lambda: {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "total_score": 0.0,
            "count": 0,
            "examples": []
        })

        for result in aspect_results:
            aspect = result["aspect"]
            sentiment = result["sentiment"]
            confidence = result.get("confidence", 0.5)

            aspect_stats[aspect][sentiment] += 1
            aspect_stats[aspect]["count"] += 1
            aspect_stats[aspect]["total_score"] += confidence

            # Store example mentions (limit to 5)
            if len(aspect_stats[aspect]["examples"]) < 5:
                aspect_stats[aspect]["examples"].append({
                    "text": result.get("context", ""),
                    "sentiment": sentiment,
                    "confidence": confidence
                })

        # Calculate statistics for each aspect
        aspects_summary = {}

        for aspect, stats in aspect_stats.items():
            total = stats["positive"] + stats["neutral"] + stats["negative"]

            if total == 0:
                continue

            # Calculate percentages
            sentiment_breakdown = {
                "positive": stats["positive"],
                "neutral": stats["neutral"],
                "negative": stats["negative"]
            }

            # Average confidence
            avg_confidence = stats["total_score"] / stats["count"] if stats["count"] > 0 else 0

            # Calculate priority score (negative % × mention count)
            negative_pct = stats["negative"] / total
            positive_pct = stats["positive"] / total
            priority_score = negative_pct * total

            # Determine priority level (more sensitive for small datasets)
            if negative_pct > 0.7:  # 70%+ negative
                priority = "high"
            elif negative_pct > 0.5 and total >= 2:  # 50%+ negative with multiple mentions
                priority = "high"
            elif negative_pct > 0.3:  # 30%+ negative
                priority = "medium"
            elif negative_pct == 0 and positive_pct > 0.5:  # Pure positive
                priority = "low"
            else:
                priority = "low"

            aspects_summary[aspect] = {
                "sentiment_breakdown": sentiment_breakdown,
                "mention_count": total,
                "confidence": round(avg_confidence, 3),
                "priority": priority,
                "priority_score": round(priority_score, 2),
                "example_mentions": stats["examples"]
            }

        # Generate summary insights
        summary = self._generate_summary(aspects_summary)

        return {
            "aspects": aspects_summary,
            "summary": summary,
            "total_aspects": len(aspects_summary),
            "total_mentions": len(aspect_results)
        }

    def _generate_summary(self, aspects_summary: Dict) -> Dict:
        """
        Generate summary insights from aspect analysis.

        Args:
            aspects_summary: Aggregated aspect statistics

        Returns:
            Dict with summary insights
        """
        if not aspects_summary:
            return {
                "top_positive_aspects": [],
                "top_negative_aspects": [],
                "priority_recommendations": []
            }

        # Sort aspects by positive sentiment
        positive_aspects = []
        negative_aspects = []

        for aspect, stats in aspects_summary.items():
            breakdown = stats["sentiment_breakdown"]
            total = sum(breakdown.values())

            if total == 0:
                continue

            positive_pct = breakdown["positive"] / total
            negative_pct = breakdown["negative"] / total

            positive_aspects.append((aspect, positive_pct, stats["mention_count"]))
            negative_aspects.append((aspect, negative_pct, stats["mention_count"]))

        # Sort by percentage
        positive_aspects.sort(key=lambda x: x[1], reverse=True)
        negative_aspects.sort(key=lambda x: x[1], reverse=True)

        # Generate recommendations for high-priority negative aspects
        recommendations = []

        for aspect, neg_pct, count in negative_aspects:
            if neg_pct > 0.5 and count >= 3:
                priority = "HIGH" if neg_pct > 0.6 else "MEDIUM"
                recommendations.append({
                    "priority": priority,
                    "aspect": aspect,
                    "action": f"Address {aspect} issues immediately",
                    "impact": f"Could improve satisfaction for {int(count * neg_pct)} customers",
                    "negative_percentage": round(neg_pct * 100, 1),
                    "mention_count": count
                })

        # Sort recommendations by priority score
        recommendations.sort(key=lambda x: (
            0 if x["priority"] == "HIGH" else 1,
            -x["mention_count"]
        ))

        return {
            "top_positive_aspects": [a[0] for a in positive_aspects[:5]],
            "top_negative_aspects": [a[0] for a in negative_aspects[:5]],
            "priority_recommendations": recommendations[:10]
        }


# Global ABSA analyzer instance
_absa_analyzer: Optional[AspectBasedSentimentAnalyzer] = None


def get_absa_analyzer() -> AspectBasedSentimentAnalyzer:
    """Get global ABSA analyzer instance."""
    global _absa_analyzer
    if _absa_analyzer is None:
        _absa_analyzer = AspectBasedSentimentAnalyzer()
    return _absa_analyzer
