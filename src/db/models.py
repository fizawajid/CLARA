"""SQLAlchemy ORM models for database tables."""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from src.db.database import Base


def generate_uuid():
    """Generate UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    feedback_batches = relationship("FeedbackBatch", back_populates="user", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class FeedbackBatch(Base):
    """Feedback batch model for uploaded feedback."""

    __tablename__ = "feedback_batches"

    id = Column(String(36), primary_key=True)  # Uses existing feedback_id format
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    total_count = Column(Integer, nullable=False)
    valid_count = Column(Integer, nullable=False)
    invalid_count = Column(Integer, nullable=False)
    upload_method = Column(String(20), nullable=True)  # 'text', 'csv', 'json'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="feedback_batches")
    analysis_results = relationship("AnalysisResult", back_populates="feedback_batch", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FeedbackBatch(id={self.id}, user_id={self.user_id}, count={self.total_count})>"


class AnalysisResult(Base):
    """Analysis result model for storing analysis outputs."""

    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    feedback_batch_id = Column(String(36), ForeignKey("feedback_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    emotion_scores = Column(JSON, nullable=True)  # Stores full emotion analysis
    topic_results = Column(JSON, nullable=True)  # Stores topic modeling results
    aspect_results = Column(JSON, nullable=True)  # Stores ABSA results (NEW)
    summary = Column(Text, nullable=True)
    key_insights = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    analysis_options = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="analysis_results")
    feedback_batch = relationship("FeedbackBatch", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, feedback_batch_id={self.feedback_batch_id})>"
