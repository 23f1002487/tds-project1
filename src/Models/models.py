"""
Pydantic models for the student application
"""
from pydantic import BaseModel, Field #type: ignore
from typing import List


class Attachment(BaseModel):
    """File attachment model"""
    name: str
    url: str


class TaskRequest(BaseModel):
    """Incoming task request model"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    secret: str = Field(..., min_length=8)
    task: str = Field(..., min_length=1)
    round: int = Field(..., ge=1)
    nonce: str = Field(..., min_length=1)
    brief: str = Field(..., min_length=1)
    checks: List[str] = Field(..., min_items=1)
    attachments: List[Attachment] = Field(default_factory=list)
    evaluation_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')


class TaskResponse(BaseModel):
    """Task completion response model"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    task: str = Field(..., min_length=1)
    round: int = Field(..., ge=1)
    nonce: str = Field(..., min_length=1)
    repo_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')
    commit_sha: str = Field(..., min_length=1)
    pages_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')


class GeneratedCode(BaseModel):
    """Generated code response from AI"""
    index_html: str = Field(..., description="Complete HTML file with proper structure")
    style_css: str = Field(..., description="Complete CSS file with styling")
    script_js: str = Field(..., description="Complete JavaScript file with functionality")
    readme_md: str = Field(..., description="Comprehensive documentation")


class CodeFile(BaseModel):
    """Individual code file model"""
    name: str
    content: str