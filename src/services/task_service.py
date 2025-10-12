"""
Task processing service - coordinates all operations.

This service orchestrates the complete task processing workflow:
1. Authentication and validation
2. AI-powered code generation
3. GitHub repository creation and file upload
4. GitHub Pages deployment
5. Evaluation URL submission

Supports both initial task processing (Round 1) and revision workflows (Round 2+).
Includes comprehensive error handling, retry logic, and logging throughout the process.
"""
import logging
import asyncio
import requests
from typing import List, Dict
from ..Models.models import TaskRequest, TaskResponse, CodeFile, GeneratedCode
from .ai_service import AIService
from .github_service import GitHubService
from ..Config.config import config


class TaskProcessor:
    """
    Main service for processing tasks through the complete workflow.
    
    Coordinates AI services, GitHub operations, and evaluation submissions
    to provide a complete task processing pipeline. Handles both initial
    task generation and revision workflows with proper error handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_service = AIService()
        self.github_service = GitHubService()
    
    def validate_credentials(self, secret: str) -> None:
        """
        Validate the provided secret key against configuration.
        
        Args:
            secret: Secret key from request
            
        Raises:
            ValueError: If secret key is invalid
        """
        if secret != config.secret_key:
            self.logger.warning("Invalid secret key provided by user")
            raise ValueError("Forbidden: Invalid secret key")
    
    async def process_task(self, task_request: TaskRequest) -> TaskResponse:
        """
        Process a complete task from request to response.
        
        Args:
            task_request: Validated task request with all required fields
            
        Returns:
            TaskResponse: Complete response with repository and deployment URLs
            
        Raises:
            Exception: For any processing errors
        """
        self.logger.info(f"Processing task: {task_request.task} (Round {task_request.round})")
        
        # Validate credentials
        self.validate_credentials(task_request.secret)
        
        try:
            if task_request.round == 1:
                return await self._process_initial_task(task_request)
            else:
                return await self._process_revision_task(task_request)
        except Exception as e:
            self.logger.error(f"Task processing failed: {e}")
            raise
    
    async def _process_initial_task(self, task_request: TaskRequest) -> TaskResponse:
        """Process initial task (round 1)"""
        # Generate code using AI
        generated_files = await self.ai_service.generate_code(
            task_request.brief,
            round_num=1,
            checks=task_request.checks,
            attachments=[attachment.dict() for attachment in task_request.attachments],
            email=task_request.email
        )
        
        # Convert to CodeFile objects
        files = [
            CodeFile(name=filename, content=content)
            for filename, content in generated_files.items()
        ]
        
        # Create GitHub repository
        repo_name = f"{task_request.task}-{task_request.nonce}"
        repo_url = self.github_service.create_repository(repo_name)
        
        # Upload files
        commit_sha = self.github_service.upload_files(repo_url, files)
        
        # Enable GitHub Pages
        pages_url = self.github_service.enable_pages(repo_url)
        
        # Submit evaluation URL
        await self._submit_evaluation_url(task_request.evaluation_url, pages_url)
        
        return TaskResponse(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
    
    async def _process_revision_task(self, task_request: TaskRequest) -> TaskResponse:
        """Process revision task (round 2+)"""
        # For round 2, we need to get existing files and revise them
        # This is a simplified implementation - in practice, you'd fetch existing files
        existing_files = {}  # Would fetch from previous round
        
        # Generate revised code
        generated_files = await self.ai_service.generate_code(
            task_request.brief,
            round_num=task_request.round,
            existing_files=existing_files,
            checks=task_request.checks,
            attachments=[attachment.dict() for attachment in task_request.attachments],
            email=task_request.email
        )
        
        # Convert to CodeFile objects
        files = [
            CodeFile(name=filename, content=content)
            for filename, content in generated_files.items()
        ]
        
        # Use existing repository or create new one
        repo_name = f"{task_request.task}-{task_request.nonce}-r{task_request.round}"
        repo_url = self.github_service.create_repository(repo_name)
        
        # Upload revised files
        commit_sha = self.github_service.upload_files(repo_url, files)
        
        # Enable GitHub Pages
        pages_url = self.github_service.enable_pages(repo_url)
        
        # Submit evaluation URL
        await self._submit_evaluation_url(task_request.evaluation_url, pages_url)
        
        return TaskResponse(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
    
    async def _submit_evaluation_url(self, evaluation_url: str, pages_url: str, max_retries: int = 3) -> None:
        """Submit the evaluation URL with retry logic"""
        self.logger.info(f"Submitting evaluation URL: {pages_url}")
        
        payload = {"url": pages_url}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(evaluation_url, json=payload, timeout=30)
                if response.status_code == 200:
                    self.logger.info("Evaluation URL submitted successfully")
                    return
                else:
                    self.logger.warning(f"Evaluation submission failed (attempt {attempt + 1}): {response.status_code}")
            except requests.RequestException as e:
                self.logger.warning(f"Evaluation submission error (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        self.logger.error("Failed to submit evaluation URL after all retries")
        raise Exception("Evaluation URL submission failed")