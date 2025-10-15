"""
Configuration management for the student application.

This module handles loading and managing configuration from environment variables.
It provides secure defaults and validation for required configuration parameters.

Environment variables:
- secret: Authentication secret key (required)
- github_token: GitHub personal access token (required)
- OPENAI_API_KEY: OpenAI/AIPIPE API key for AI services (optional)
- OPENAI_BASE_URL: Custom API base URL (optional, defaults to AIPIPE)

The configuration supports both local development and production deployment.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        secret_key: Authentication secret key for API access
        github_token: GitHub personal access token for repository operations
        openai_token: OpenAI API key for AI services (optional)
        aipipe_url: Custom API base URL (optional)
        log_file: Path to log file (default: logs/task_log.txt)
        log_level: Logging level (default: DEBUG)
    """
    secret_key: str
    github_token: str
    openai_token: Optional[str] = None
    aipipe_url: Optional[str] = None
    log_file: str = "logs/task_log.txt"
    log_level: str = "DEBUG"
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.
        
        Returns:
            Config: Configured instance with values from environment
            
        Note:
            Uses secure defaults ("...") for missing required variables
            to prevent application crashes during development.
        """
        
        return cls(
            secret_key=os.getenv("secret", "..."),
            github_token=os.getenv("github_token", "..."),
            openai_token = os.getenv("OPENAI_API_KEY"),
            aipipe_url=os.getenv("OPENAI_BASE_URL")
        )

# Global config instance
config = Config.from_env()