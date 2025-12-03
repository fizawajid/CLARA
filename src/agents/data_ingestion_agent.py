"""Data Ingestion Agent - Validates and preprocesses feedback data."""

import re
import uuid
from typing import Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.llms.fake import FakeListLLM

from src.services.vectorstore import get_vector_store_service
from src.utils.config import get_config
from src.utils.logging_config import LogExecutionTime, get_logger

logger = get_logger(__name__)


class DataIngestionAgent:
    """Agent responsible for validating and ingesting feedback data."""

    def __init__(self):
        """Initialize Data Ingestion Agent."""
        self.config = get_config()
        self.vector_store = get_vector_store_service()
        logger.info("Data Ingestion Agent initialized")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text input

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove special characters but keep punctuation
        text = re.sub(r"[^\w\s\.,!?;:\-\'\"()]", "", text)

        # Remove URLs
        text = re.sub(r"http\S+|www.\S+", "", text)

        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)

        return text.strip()

    def validate_feedback(self, feedback: List[str]) -> Dict:
        """
        Validate feedback entries.

        Args:
            feedback: List of feedback texts

        Returns:
            Dict: Validation results with valid/invalid entries
        """
        logger.info(f"Validating {len(feedback)} feedback entries")

        valid_entries = []
        invalid_entries = []
        cleaned_entries = []

        for idx, entry in enumerate(feedback):
            # Check if entry is empty
            if not entry or not entry.strip():
                invalid_entries.append({
                    "index": idx,
                    "reason": "Empty entry",
                    "original": entry,
                })
                continue

            # Check minimum length (at least 3 words)
            word_count = len(entry.split())
            if word_count < 3:
                invalid_entries.append({
                    "index": idx,
                    "reason": f"Too short ({word_count} words)",
                    "original": entry,
                })
                continue

            # Clean the text
            cleaned = self.clean_text(entry)

            # Check if cleaning removed too much
            if not cleaned or len(cleaned) < 10:
                invalid_entries.append({
                    "index": idx,
                    "reason": "Invalid content after cleaning",
                    "original": entry,
                })
                continue

            # Valid entry
            valid_entries.append({
                "index": idx,
                "original": entry,
                "cleaned": cleaned,
            })
            cleaned_entries.append(cleaned)

        logger.info(
            f"Validation complete: {len(valid_entries)} valid, "
            f"{len(invalid_entries)} invalid"
        )

        return {
            "valid_entries": valid_entries,
            "invalid_entries": invalid_entries,
            "cleaned_texts": cleaned_entries,
            "valid_count": len(valid_entries),
            "invalid_count": len(invalid_entries),
        }

    def ingest_feedback(
        self,
        feedback: List[str],
        metadata: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Ingest and store feedback in vector database.

        Args:
            feedback: List of feedback texts
            metadata: Optional metadata for each feedback

        Returns:
            Dict: Ingestion results with feedback ID and stats
        """
        with LogExecutionTime(logger, "Feedback ingestion"):
            # Validate and clean feedback
            validation_result = self.validate_feedback(feedback)

            if validation_result["valid_count"] == 0:
                logger.error("No valid feedback entries to ingest")
                return {
                    "success": False,
                    "error": "No valid feedback entries",
                    "validation": validation_result,
                }

            # Generate feedback batch ID
            feedback_id = f"feedback_{uuid.uuid4().hex[:12]}"

            # Prepare metadata
            cleaned_texts = validation_result["cleaned_texts"]
            if metadata is None:
                metadata = []

            # Add batch ID to metadata
            enriched_metadata = []
            for idx, entry in enumerate(validation_result["valid_entries"]):
                meta = metadata[entry["index"]] if entry["index"] < len(metadata) else {}
                meta.update({
                    "feedback_id": feedback_id,
                    "original_index": entry["index"],
                    "text": entry["cleaned"],
                })
                enriched_metadata.append(meta)

            # Store in vector database
            try:
                doc_ids = self.vector_store.add_documents(
                    documents=cleaned_texts,
                    metadata=enriched_metadata,
                )

                logger.info(
                    f"Ingested {len(doc_ids)} documents with feedback_id: {feedback_id}"
                )

                return {
                    "success": True,
                    "feedback_id": feedback_id,
                    "document_ids": doc_ids,
                    "ingested_count": len(doc_ids),
                    "validation": validation_result,
                }

            except Exception as e:
                logger.error(f"Error storing feedback in vector database: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "validation": validation_result,
                }

    def get_feedback_by_id(self, feedback_id: str) -> Dict:
        """
        Retrieve feedback by batch ID.

        Args:
            feedback_id: Feedback batch ID

        Returns:
            Dict: Feedback documents and metadata
        """
        try:
            # Search for documents with this feedback_id
            # Note: ChromaDB doesn't have direct metadata filtering,
            # so we retrieve all and filter
            all_docs = self.vector_store.get_all_documents()

            matching_docs = []
            matching_metadata = []

            for idx, meta in enumerate(all_docs["metadatas"]):
                if meta.get("feedback_id") == feedback_id:
                    matching_docs.append(all_docs["documents"][idx])
                    matching_metadata.append(meta)

            logger.info(f"Found {len(matching_docs)} documents for feedback_id: {feedback_id}")

            return {
                "feedback_id": feedback_id,
                "documents": matching_docs,
                "metadata": matching_metadata,
                "count": len(matching_docs),
            }

        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return {
                "feedback_id": feedback_id,
                "documents": [],
                "metadata": [],
                "count": 0,
                "error": str(e),
            }

    def get_statistics(self) -> Dict:
        """
        Get ingestion statistics.

        Returns:
            Dict: Statistics about ingested data
        """
        stats = self.vector_store.get_stats()
        return {
            "total_documents": stats["document_count"],
            "collection_name": stats["collection_name"],
        }


# Global agent instance
_data_ingestion_agent: Optional[DataIngestionAgent] = None


def get_data_ingestion_agent() -> DataIngestionAgent:
    """
    Get global Data Ingestion Agent instance.

    Returns:
        DataIngestionAgent: Global agent instance
    """
    global _data_ingestion_agent
    if _data_ingestion_agent is None:
        _data_ingestion_agent = DataIngestionAgent()
    return _data_ingestion_agent
