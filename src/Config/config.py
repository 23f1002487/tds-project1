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
    aipipe_token: Optional[str] = None
    aipipe_url: Optional[str] = None
    # Keep legacy OpenAI field for backward compatibility
    openai_api_key: Optional[str] = None
    openai_url: Optional[str] = None
    log_file: str = "task_log.txt"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        # Get AIPIPE_TOKEN
        aipipe_token = os.getenv("AIPIPE_TOKEN")
        
        # If we have AIPIPE_TOKEN but no OPENAI_API_KEY, set OPENAI_API_KEY to AIPIPE_TOKEN
        # This allows pydantic-ai to work with AIPIPE
        if aipipe_token and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = aipipe_token
        
        return cls(
            secret_key=os.getenv("secret", "..."),
            github_token=os.getenv("github_token", "..."),
            aipipe_token=aipipe_token,
            aipipe_url=os.getenv("AIPIPE_URL", "https://aipipe.org/openai/v1"),
            # Legacy OpenAI support
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_url=os.getenv("OPENAI_URL", "https://api.openai.com/v1"),
            log_file=os.getenv("LOG_FILE", "/tmp/task_log.txt"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    @property
    def has_ai_key(self) -> bool:
        """Check if AI API key is available (AIPIPE or OpenAI)"""
        return bool(
            (self.aipipe_token and self.aipipe_token.strip()) or
            (self.openai_api_key and self.openai_api_key.strip())
        )
    
    @property
    def get_ai_key(self) -> Optional[str]:
        """Get the appropriate AI API key (prioritize AIPIPE)"""
        if self.aipipe_token and self.aipipe_token.strip():
            return self.aipipe_token
        return self.openai_api_key
    
    @property
    def get_ai_url(self) -> str:
        """Get the appropriate AI API URL (prioritize AIPIPE)"""
        if self.aipipe_token and self.aipipe_token.strip():
            return self.aipipe_url or "https://aipipe.org/openrouter/v1"
        return self.openai_url or "https://api.openai.com/v1"
    
    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is available"""
        return bool(self.openai_api_key and self.openai_api_key.strip())


# Global config instance
config = Config.from_env()