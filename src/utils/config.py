"""Configuration management for the NLP Agentic AI system."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    """Model configuration."""
    model_config = SettingsConfigDict(env_prefix='', extra='ignore')

    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    spacy_model: str = Field(default="en_core_web_sm")
    embedding_dimension: int = Field(default=384)


class ChromaDBConfig(BaseSettings):
    """ChromaDB configuration."""
    model_config = SettingsConfigDict(env_prefix='CHROMA_', extra='ignore')

    persist_directory: str = Field(default="./chroma_db", alias='persist_dir')
    collection_name: str = Field(default="feedback_embeddings")


class APIConfig(BaseSettings):
    """API configuration."""
    model_config = SettingsConfigDict(env_prefix='API_', extra='ignore')

    title: str = Field(default="NLP Agentic AI Feedback Analysis System")
    description: str = Field(default="Multi-agent system for feedback analysis")
    version: str = Field(default="1.0.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=4)
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])


class AgentConfig(BaseSettings):
    """Agent configuration."""
    model_config = SettingsConfigDict(env_prefix='AGENT_', extra='ignore')

    max_retries: int = Field(default=3)
    timeout: int = Field(default=300)
    verbose: bool = Field(default=True)


class NLPConfig(BaseSettings):
    """NLP processing configuration."""
    model_config = SettingsConfigDict(env_prefix='', extra='ignore')

    min_topic_size: int = Field(default=5)
    max_topics: int = Field(default=10)
    sentiment_threshold: float = Field(default=0.05)
    summary_ratio: float = Field(default=0.2)


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    model_config = SettingsConfigDict(env_prefix='LOG_', extra='ignore')

    level: str = Field(default="INFO")
    format: str = Field(default="json")
    log_file: str = Field(default="./logs/app.log", alias='file')
    max_file_size: int = Field(default=10485760)
    backup_count: int = Field(default=5)


class Config(BaseSettings):
    """Main configuration class."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore',  # Ignore extra environment variables
        case_sensitive=False
    )

    models: ModelConfig = Field(default_factory=ModelConfig)
    chromadb: ChromaDBConfig = Field(default_factory=ChromaDBConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    nlp: NLPConfig = Field(default_factory=NLPConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to configuration YAML file. Defaults to config.yaml

    Returns:
        Config: Configuration object
    """
    if config_path is None:
        config_path = os.path.join(os.getcwd(), "config.yaml")

    config_dict: Dict[str, Any] = {}

    # Load from YAML file if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}

    # Create sub-configurations with both YAML and env var support
    models = ModelConfig(**config_dict.get("models", {}))
    chromadb = ChromaDBConfig(**config_dict.get("chromadb", {}))
    api = APIConfig(**config_dict.get("api", {}))
    agents = AgentConfig(**config_dict.get("agents", {}))
    nlp = NLPConfig(**config_dict.get("nlp", {}))
    logging_config = LoggingConfig(**config_dict.get("logging", {}))

    config = Config(
        models=models,
        chromadb=chromadb,
        api=api,
        agents=agents,
        nlp=nlp,
        logging=logging_config
    )

    # Ensure directories exist
    Path(config.chromadb.persist_directory).mkdir(parents=True, exist_ok=True)
    log_dir = Path(config.logging.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    return config


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Config: Global configuration object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """
    Reload configuration from file.

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Config: Reloaded configuration object
    """
    global _config
    _config = load_config(config_path)
    return _config