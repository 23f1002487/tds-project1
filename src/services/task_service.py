"""
Task processing service - coordinates all operations.

This service orchestrates the complete task processing workflow:
1. Authentication and validation
2. Immediate response to client
3. Background AI-powered code generation
4. GitHub repository creation and file upload
5. GitHub Pages deployment
6. Evaluation URL submission with complete results

Supports both initial task processing (Round 1) and revision workflows (Round 2+).
Uses async background processing to provide immediate responses while handling
long-running AI operations behind the scenes.
"""
import logging
import asyncio
import requests
import uuid
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..Models.models import TaskRequest, TaskResponse, CodeFile, GeneratedCode
from .ai_service import AIService
from .github_service import GitHubService
from ..Config.config import config


class TaskProcessor:
    """
    Main service for processing tasks through the complete workflow.
    
    Provides immediate responses to clients while processing tasks in the background.
    Coordinates AI services, GitHub operations, and evaluation submissions with
    proper error handling and status tracking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_service = AIService()
        self.github_service = GitHubService()
        # Track background tasks
        self.processing_tasks: Dict[str, dict] = {}
    
    def _post_with_retry(self, url: str, payload: dict, max_retries: int = 3, timeout: int = 30) -> Optional[requests.Response]:
        """
        POST request with exponential backoff retry for transient failures.
        
        Args:
            url: URL to POST to
            payload: JSON payload
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            Response object if successful, None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=timeout)
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    self.logger.warning(f"Network error on attempt {attempt + 1}/{max_retries}: {e}")
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All {max_retries} attempts failed: {e}")
                    raise
            except requests.RequestException as e:
                # Non-retryable error
                self.logger.error(f"Non-retryable request error: {e}")
                raise
        return None
    
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
    
    async def process_task(self, task_request: TaskRequest) -> dict:
        """
        Process a task with immediate response and background processing.
        
        Args:
            task_request: Validated task request with all required fields
            
        Returns:
            dict: Immediate response with processing status and tracking info
        """
        self.logger.info(f"Processing task: {task_request.task} (Round {task_request.round})")
        
        # Validate credentials immediately
        self.validate_credentials(task_request.secret)
        
        # Generate processing ID for tracking
        processing_id = f"{task_request.task}-{task_request.nonce}-{task_request.round}-{uuid.uuid4().hex[:8]}"
        
        # Store task info for tracking
        self.processing_tasks[processing_id] = {
            "status": "processing",
            "started_at": datetime.now(),
            "task_request": task_request,
            "estimated_completion": datetime.now() + timedelta(seconds=45)
        }
        
        # Start background processing (don't await!)
        asyncio.create_task(self._process_task_background(processing_id, task_request))
        
        # Return immediate response
        return {
            "status": "accepted",
            "message": "Task processing started successfully",
            "processing_id": processing_id,
            "nonce": task_request.nonce,
            "task": task_request.task,
            "round": task_request.round,
            "estimated_completion_time": "30-45 seconds",
            "started_at": datetime.now().isoformat()
        }
    
    async def _process_task_background(self, processing_id: str, task_request: TaskRequest) -> None:
        """
        Background task processing that happens after immediate response.
        
        Args:
            processing_id: Unique identifier for tracking this processing task
            task_request: The original task request to process
        """
        try:
            self.logger.info(f"Starting background processing for {processing_id}")
            
            # Update status
            if processing_id in self.processing_tasks:
                self.processing_tasks[processing_id]["status"] = "generating_code"
            
            # Process the task based on round
            if task_request.round == 1:
                result = await self._process_initial_task_background(task_request)
            else:
                result = await self._process_revision_task_background(task_request)
            
            # Update status to completed
            if processing_id in self.processing_tasks:
                self.processing_tasks[processing_id].update({
                    "status": "completed",
                    "completed_at": datetime.now(),
                    "result": result
                })
            
            # Submit complete results to evaluation URL
            await self._submit_complete_results(task_request.evaluation_url, result)
            
            self.logger.info(f"Background processing completed for {processing_id}")
            
        except Exception as e:
            self.logger.error(f"Background processing failed for {processing_id}: {e}")
            
            # Update status to failed
            if processing_id in self.processing_tasks:
                self.processing_tasks[processing_id].update({
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.now()
                })
            
            # Try to notify evaluation URL about failure
            try:
                await self._submit_error_results(task_request.evaluation_url, task_request, str(e))
            except Exception as submit_error:
                self.logger.error(f"Failed to submit error results: {submit_error}")
    
    async def _process_initial_task_background(self, task_request: TaskRequest) -> TaskResponse:
        """Process initial task (round 1) in background"""
        self.logger.info(f"Generating code for {task_request.task}")
        
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
        
        return TaskResponse(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
    
    async def _process_revision_task_background(self, task_request: TaskRequest) -> TaskResponse:
        """Process revision task (round 2+) in background"""
        self.logger.info(f"Revising code for {task_request.task} (Round {task_request.round})")
        
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
        
        return TaskResponse(
            email=task_request.email,
            task=task_request.task,
            round=task_request.round,
            nonce=task_request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
    
    async def _submit_complete_results(self, evaluation_url: str, result: TaskResponse) -> None:
        """Submit the complete results to the evaluation URL"""
        self.logger.info(f"Submitting complete results to evaluation URL: {evaluation_url}")
        
        payload = {
            "email": result.email,
            "task": result.task,
            "round": result.round,
            "nonce": result.nonce,
            "repo_url": result.repo_url,
            "commit_sha": result.commit_sha,
            "pages_url": result.pages_url,
            "status": "completed"
        }
        
        try:
            response = self._post_with_retry(evaluation_url, payload, max_retries=3, timeout=30)
            if response and response.status_code == 200:
                self.logger.info("Complete results submitted successfully")
            elif response:
                self.logger.warning(f"Failed to submit complete results: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Network error submitting complete results (DNS/connection failed): {e}")
            self.logger.info("Task processing completed successfully but evaluation notification failed due to network issues")
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout submitting complete results: {e}")
            self.logger.info("Task processing completed successfully but evaluation notification timed out")
        except requests.RequestException as e:
            self.logger.error(f"Error submitting complete results: {e}")
    
    async def _submit_error_results(self, evaluation_url: str, task_request: TaskRequest, error_message: str) -> None:
        """Submit error results to the evaluation URL"""
        self.logger.info(f"Submitting error results to evaluation URL: {evaluation_url}")
        
        payload = {
            "email": task_request.email,
            "task": task_request.task,
            "round": task_request.round,
            "nonce": task_request.nonce,
            "status": "failed",
            "error": error_message
        }
        
        try:
            response = self._post_with_retry(evaluation_url, payload, max_retries=3, timeout=30)
            if response and response.status_code == 200:
                self.logger.info("Error results submitted successfully")
            elif response:
                self.logger.warning(f"Failed to submit error results: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Network error submitting error results (DNS/connection failed): {e}")
            self.logger.info("Task processing completed but evaluation notification failed due to network issues")
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout submitting error results: {e}")
            self.logger.info("Task processing completed but evaluation notification timed out")
        except requests.RequestException as e:
            self.logger.error(f"Error submitting error results: {e}")