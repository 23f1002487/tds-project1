"""
Configuration management for the student application
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration"""
    secret_key: str
    github_token: str
    openai_token: Optional[str] = None
    aipipe_url: Optional[str] = None
    log_file: str = "task_log.txt"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        
        return cls(
            secret_key=os.getenv("secret", "..."),
            github_token=os.getenv("github_token", "..."),
            openai_token = os.getenv("OPENAI_API_KEY"),
            aipipe_url=os.getenv("OPENAI_BASE_URL")
        )

# Global config instance
config = Config.from_env()