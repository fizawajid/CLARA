"""
API Client Wrapper for FastAPI Backend Communication
"""

import httpx
from typing import Dict, List, Optional, Any
import time
from datetime import datetime


class APIClient:
    """
    Singleton client for communicating with CLARA NLP FastAPI backend
    """

    _instance = None

    def __new__(cls, base_url: str = "http://localhost:8000"):
        if cls._instance is None:
            cls._instance = super(APIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: str = "http://localhost:8000"):
        if self._initialized:
            return

        self.base_url = base_url.rstrip('/')
        self.timeout = 300.0  # 5 minutes timeout for long-running analyses
        self._initialized = True

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers from session state.

        Returns:
            Headers dict with Bearer token if authenticated
        """
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and st.session_state.get('access_token'):
                return {"Authorization": f"Bearer {st.session_state.access_token}"}
        except:
            pass
        return {}

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: JSON data for request body
            params: Query parameters
            headers: Additional headers (auth headers added automatically)
            max_retries: Maximum number of retry attempts

        Returns:
            Response data as dictionary

        Raises:
            Exception: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        # Merge auth headers with provided headers
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)

        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = client.get(url, params=params, headers=request_headers)
                    elif method.upper() == "POST":
                        response = client.post(url, json=data, params=params, headers=request_headers)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    # Retry on server errors
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    # Client error or final retry - raise with details
                    try:
                        error_detail = e.response.json()
                    except:
                        error_detail = {"error": str(e)}
                    raise Exception(f"API Error ({e.response.status_code}): {error_detail}")

            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception(f"Connection Error: {str(e)}. Make sure the API server is running on {self.base_url}")

            except Exception as e:
                raise Exception(f"Unexpected Error: {str(e)}")

        raise Exception("Max retries exceeded")

    def get_health(self) -> Dict[str, Any]:
        """
        Get API health status

        Returns:
            Health status information
        """
        return self._make_request("GET", "/health")

    def get_info(self) -> Dict[str, Any]:
        """
        Get system information

        Returns:
            System configuration and model info
        """
        return self._make_request("GET", "/info")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics

        Returns:
            Document counts and stats
        """
        return self._make_request("GET", "/api/v1/statistics")

    def get_emotion_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent emotion analysis history for the current user

        Args:
            limit: Maximum number of history items to return

        Returns:
            Dict containing history list
        """
        return self._make_request("GET", "/api/v1/history/emotions", params={"limit": limit})

    def get_analysis_history(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent full analysis history (including topics) for the current user

        Args:
            limit: Maximum number of history items to return

        Returns:
            Dict containing history list
        """
        return self._make_request("GET", "/api/v1/history/analyses", params={"limit": limit})

    def upload_feedback(
        self,
        feedback: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Upload feedback data

        Args:
            feedback: List of feedback text strings
            metadata: Optional list of metadata dictionaries

        Returns:
            Upload response with feedback_id
        """
        data = {
            "feedback": feedback
        }
        if metadata:
            data["metadata"] = metadata

        return self._make_request("POST", "/api/v1/upload", data=data)

    def analyze_feedback(
        self,
        feedback_id: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze uploaded feedback

        Args:
            feedback_id: ID of uploaded feedback batch
            options: Analysis options (include_summary, include_topics, etc.)

        Returns:
            Analysis results (sentiment, topics, report)
        """
        data = {
            "feedback_id": feedback_id
        }
        if options:
            data["options"] = options

        return self._make_request("POST", "/api/v1/analyze", data=data)

    def process_feedback(
        self,
        feedback: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Upload and analyze feedback in one step

        Args:
            feedback: List of feedback text strings
            metadata: Optional list of metadata dictionaries

        Returns:
            Complete analysis results
        """
        data = {
            "feedback": feedback
        }
        if metadata:
            data["metadata"] = metadata

        return self._make_request("POST", "/api/v1/process", data=data)

    def get_feedback_summary(self, feedback_id: str) -> Dict[str, Any]:
        """
        Get summary of uploaded feedback

        Args:
            feedback_id: ID of feedback batch

        Returns:
            Feedback summary with samples
        """
        return self._make_request("GET", f"/api/v1/feedback/{feedback_id}")

    def get_aspect_history(
        self,
        aspect: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get aspect-based sentiment analysis history

        Args:
            aspect: Optional aspect name to filter by
            limit: Maximum number of history items to return

        Returns:
            Dict containing aspect analysis history
        """
        params = {"limit": limit}
        if aspect:
            params["aspect"] = aspect
        return self._make_request("GET", "/api/v1/history/aspects", params=params)

    def get_aspect_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get aggregated aspect sentiment summary

        Args:
            days: Number of days to include in summary (default 30)

        Returns:
            Dict containing aspect summary with sentiment breakdown and recommendations
        """
        return self._make_request("GET", "/api/v1/aspects/summary", params={"days": days})

    def check_connection(self) -> bool:
        """
        Check if API server is reachable

        Returns:
            True if connected, False otherwise
        """
        try:
            self.get_health()
            return True
        except:
            return False


# Global singleton instance
def get_api_client(base_url: str = "http://localhost:8000") -> APIClient:
    """
    Get or create API client singleton instance

    Args:
        base_url: Base URL of the API server

    Returns:
        APIClient instance
    """
    return APIClient(base_url)
