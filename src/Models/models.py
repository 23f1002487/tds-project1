"""
Pydantic models for the student application.

This module defines all the data models used throughout the application:
- Request/response models for API endpoints
- File and code generation models
- Validation and serialization schemas

All models include comprehensive validation rules and documentation
to ensure data integrity and API contract compliance.
"""
from pydantic import BaseModel, Field #type: ignore
from typing import List


class Attachment(BaseModel):
    """
    File attachment model for task requests.
    
    Supports both URL references and base64-encoded content
    for file attachments in task processing.
    """
    name: str
    url: str


class TaskRequest(BaseModel):
    """
    Incoming task request model with comprehensive validation.
    
    Validates email format, authentication, and task requirements
    according to the evaluation framework specifications.
    """
    email: str = Field(..., pattern=r'^23f\d{7}@ds\.study\.iitm\.ac\.in$')
    secret: str = Field(..., min_length=8)
    task: str = Field(..., min_length=1)
    round: int = Field(..., ge=1)
    nonce: str = Field(..., min_length=1)
    brief: str = Field(..., min_length=1)
    checks: List[str] = Field(..., min_items=1)
    attachments: List[Attachment] = Field(default_factory=list)
    evaluation_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')


class TaskResponse(BaseModel):
    """
    Task completion response model.
    
    Contains all the information about the completed task including
    repository details, deployment URLs, and processing metadata.
    """
    email: str = Field(..., pattern=r'^23f\d{7}@ds\.study\.iitm\.ac\.in$')
    task: str = Field(..., min_length=1)
    round: int = Field(..., ge=1)
    nonce: str = Field(..., min_length=1)
    repo_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')
    commit_sha: str = Field(..., min_length=1)
    pages_url: str = Field(..., pattern=r'^https?://[^\s/$.?#].[^\s]*$')


class GeneratedCode(BaseModel):
    """
    Generated code response from AI with validation.
    
    Ensures all required files are generated with proper content
    for complete web application functionality.
    """
    index_html: str = Field(..., description="Complete HTML file with proper structure")
    style_css: str = Field(..., description="Complete CSS file with styling")
    script_js: str = Field(..., description="Complete JavaScript file with functionality")
    readme_md: str = Field(..., description="Comprehensive documentation")


class CodeFile(BaseModel):
    """
    Individual code file model for repository operations.
    
    Represents a single file with name and content for
    upload to GitHub repositories.
    """
    name: str
    content: str