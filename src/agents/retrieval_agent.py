"""Retrieval Agent - RAG-based semantic search and context retrieval."""

from typing import Dict, List, Optional

from src.services.vectorstore import get_vector_store_service
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class RetrievalAgent:
    """Agent responsible for semantic search and RAG operations."""

    def __init__(self):
        """Initialize Retrieval Agent."""
        self.config = get_config()
        self.vector_store = get_vector_store_service()
        logger.info("Retrieval Agent initialized")

    def retrieve_similar(
        self,
        query: str,
        n_results: int = 5,
        feedback_id: Optional[str] = None,
    ) -> Dict:
        """
        Retrieve similar documents using semantic search.

        Args:
            query: Query text for similarity search
            n_results: Number of results to return
            feedback_id: Optional feedback batch ID to filter by

        Returns:
            Dict: Retrieved documents with similarity scores
        """
        logger.info(f"Retrieving {n_results} similar documents for query")

        with LogExecutionTime(logger, "Semantic retrieval"):
            try:
                # Perform semantic search
                results = self.vector_store.search(
                    query=query,
                    n_results=n_results,
                )

                # Filter by feedback_id if provided
                if feedback_id:
                    filtered_docs = []
                    filtered_distances = []
                    filtered_metadata = []
                    filtered_ids = []

                    for idx, meta in enumerate(results["metadatas"]):
                        if meta.get("feedback_id") == feedback_id:
                            filtered_docs.append(results["documents"][idx])
                            filtered_distances.append(results["distances"][idx])
                            filtered_metadata.append(meta)
                            filtered_ids.append(results["ids"][idx])

                    results = {
                        "documents": filtered_docs,
                        "distances": filtered_distances,
                        "metadatas": filtered_metadata,
                        "ids": filtered_ids,
                    }

                logger.info(f"Retrieved {len(results['documents'])} documents")

                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "count": len(results["documents"]),
                }

            except Exception as e:
                logger.error(f"Error during retrieval: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "results": {
                        "documents": [],
                        "distances": [],
                        "metadatas": [],
                        "ids": [],
                    },
                }

    def retrieve_context_for_topics(
        self,
        topics: List[Dict],
        n_results_per_topic: int = 3,
        feedback_id: Optional[str] = None,
    ) -> Dict:
        """
        Retrieve relevant context for discovered topics.

        Args:
            topics: List of topic dictionaries with keywords
            n_results_per_topic: Number of documents per topic
            feedback_id: Optional feedback batch ID to filter by

        Returns:
            Dict: Context for each topic
        """
        logger.info(f"Retrieving context for {len(topics)} topics")

        topic_contexts = {}

        for topic in topics:
            topic_id = topic.get("topic_id")
            keywords = topic.get("keywords", [])

            if not keywords:
                continue

            # Create query from top keywords
            query = " ".join(keywords[:5])

            # Retrieve relevant documents
            retrieval_result = self.retrieve_similar(
                query=query,
                n_results=n_results_per_topic,
                feedback_id=feedback_id,
            )

            if retrieval_result["success"]:
                topic_contexts[topic_id] = {
                    "keywords": keywords,
                    "context_documents": retrieval_result["results"]["documents"],
                    "relevance_scores": retrieval_result["results"]["distances"],
                }

        logger.info(f"Retrieved context for {len(topic_contexts)} topics")

        return {
            "topic_contexts": topic_contexts,
            "topics_processed": len(topic_contexts),
        }

    def retrieve_by_sentiment(
        self,
        sentiment_label: str,
        feedback_id: str,
        n_results: int = 10,
    ) -> Dict:
        """
        Retrieve documents by sentiment (requires sentiment in metadata).

        Args:
            sentiment_label: Sentiment label (positive, negative, neutral)
            feedback_id: Feedback batch ID
            n_results: Number of results

        Returns:
            Dict: Documents matching sentiment
        """
        logger.info(f"Retrieving {sentiment_label} feedback documents")

        try:
            # Get all documents for this feedback_id
            all_docs = self.vector_store.get_all_documents()

            matching_docs = []
            matching_metadata = []

            for idx, meta in enumerate(all_docs["metadatas"]):
                if (
                    meta.get("feedback_id") == feedback_id
                    and meta.get("sentiment") == sentiment_label
                ):
                    matching_docs.append(all_docs["documents"][idx])
                    matching_metadata.append(meta)

                    if len(matching_docs) >= n_results:
                        break

            logger.info(f"Found {len(matching_docs)} {sentiment_label} documents")

            return {
                "success": True,
                "sentiment": sentiment_label,
                "documents": matching_docs,
                "metadata": matching_metadata,
                "count": len(matching_docs),
            }

        except Exception as e:
            logger.error(f"Error retrieving by sentiment: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documents": [],
            }

    def get_representative_samples(
        self,
        feedback_id: str,
        n_samples: int = 5,
    ) -> Dict:
        """
        Get representative sample documents from a feedback batch.

        Args:
            feedback_id: Feedback batch ID
            n_samples: Number of samples to return

        Returns:
            Dict: Representative sample documents
        """
        logger.info(f"Getting {n_samples} representative samples")

        try:
            # Get all documents for this feedback_id
            all_docs = self.vector_store.get_all_documents()

            matching_docs = []
            matching_ids = []

            for idx, meta in enumerate(all_docs["metadatas"]):
                if meta.get("feedback_id") == feedback_id:
                    matching_docs.append(all_docs["documents"][idx])
                    matching_ids.append(all_docs["ids"][idx])

            # Select evenly distributed samples
            if len(matching_docs) <= n_samples:
                samples = matching_docs
            else:
                # Select evenly spaced samples
                indices = [
                    int(i * len(matching_docs) / n_samples)
                    for i in range(n_samples)
                ]
                samples = [matching_docs[i] for i in indices]

            logger.info(f"Selected {len(samples)} representative samples")

            return {
                "success": True,
                "samples": samples,
                "total_documents": len(matching_docs),
                "sample_count": len(samples),
            }

        except Exception as e:
            logger.error(f"Error getting representative samples: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "samples": [],
            }

    def augment_with_context(
        self,
        query: str,
        context_window: int = 3,
        feedback_id: Optional[str] = None,
    ) -> str:
        """
        Augment a query with retrieved context (RAG pattern).

        Args:
            query: Original query
            context_window: Number of context documents
            feedback_id: Optional feedback batch ID

        Returns:
            str: Augmented prompt with context
        """
        logger.info("Augmenting query with retrieved context")

        # Retrieve relevant context
        retrieval_result = self.retrieve_similar(
            query=query,
            n_results=context_window,
            feedback_id=feedback_id,
        )

        if not retrieval_result["success"]:
            logger.warning("Context retrieval failed, using original query")
            return query

        # Build augmented prompt
        context_docs = retrieval_result["results"]["documents"]

        if not context_docs:
            return query

        augmented_prompt = f"""Based on the following context documents:

"""
        for idx, doc in enumerate(context_docs, 1):
            augmented_prompt += f"{idx}. {doc}\n\n"

        augmented_prompt += f"\nQuery: {query}"

        logger.info(f"Augmented query with {len(context_docs)} context documents")

        return augmented_prompt


# Global agent instance
_retrieval_agent: Optional[RetrievalAgent] = None


def get_retrieval_agent() -> RetrievalAgent:
    """
    Get global Retrieval Agent instance.

    Returns:
        RetrievalAgent: Global agent instance
    """
    global _retrieval_agent
    if _retrieval_agent is None:
        _retrieval_agent = RetrievalAgent()
    return _retrieval_agent
