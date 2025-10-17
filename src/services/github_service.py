"""
GitHub service for repository operations.

This service handles all GitHub-related operations including:
- Repository creation with proper configuration
- File upload with base64 encoding
- GitHub Pages deployment and configuration
- Error handling and retry logic

Requires a valid GitHub personal access token with appropriate permissions:
- repo (for repository creation and file operations)
- pages (for GitHub Pages deployment)
"""
import logging
import requests
import base64
from typing import List, Dict
from ..Models.models import CodeFile
from ..Config.config import config


class GitHubService:
    """
    Service for GitHub repository operations.
    
    Handles repository creation, file uploads, and GitHub Pages deployment
    using the GitHub REST API. Includes comprehensive error handling and
    logging for all operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.token = config.github_token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_repository(self, repo_name: str) -> str:
        """
        Create a GitHub repository and return the repository URL.
        Handles duplicate repository names by adding unique suffixes.
        
        Args:
            repo_name: Name for the new repository
            
        Returns:
            str: HTML URL of the created repository
            
        Raises:
            Exception: If repository creation fails after all retries
        """
        import random
        import time
        
        original_name = repo_name
        max_attempts = 5
        
        for attempt in range(1, max_attempts + 1):
            current_name = repo_name
            
            if attempt > 1:
                # Generate unique suffix for retry attempts
                timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
                random_suffix = random.randint(1000, 9999)
                current_name = f"{original_name}-{timestamp}-{random_suffix}"
                self.logger.warning(f"Repository name conflict detected. Attempt {attempt}/{max_attempts} with new name: {current_name}")
            else:
                self.logger.info(f"Creating GitHub repository: {current_name}")
            
            payload = {
                "name": current_name,
                "private": False,
                "auto_init": True,
                "license_template": "mit"
            }
            
            response = requests.post(
                "https://api.github.com/user/repos",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                repo_url = response.json()["html_url"]
                if attempt > 1:
                    self.logger.info(f"GitHub repository created successfully with alternative name: {repo_url}")
                    self.logger.info(f"Original name '{original_name}' was already taken, used '{current_name}' instead")
                else:
                    self.logger.info(f"GitHub repository created successfully: {repo_url}")
                return repo_url
            
            # Check if it's a duplicate name error
            response_data = response.json()
            is_duplicate = False
            
            if response.status_code == 422 and "errors" in response_data:
                for error in response_data["errors"]:
                    if error.get("field") == "name" and "already exists" in error.get("message", "").lower():
                        is_duplicate = True
                        break
            
            if is_duplicate:
                self.logger.warning(f"Repository name '{current_name}' already exists. Will retry with unique suffix...")
                time.sleep(0.5)  # Small delay before retry
                continue
            else:
                # Different error, don't retry
                self.logger.error(f"Failed to create GitHub repository: {response_data}")
                raise Exception(f"GitHub repository creation failed: {response_data.get('message', 'Unknown error')}")
        
        # All attempts exhausted
        self.logger.error(f"Failed to create repository after {max_attempts} attempts")
        raise Exception(f"GitHub repository creation failed: Unable to generate unique repository name after {max_attempts} attempts")
    
    def upload_files(self, repo_url: str, files: List[CodeFile]) -> str:
        """Upload files to GitHub repository and return commit SHA"""
        self.logger.info(f"Uploading {len(files)} files to repository")
        
        repo_name = repo_url.split("github.com/")[-1]
        commit_sha = ""
        
        for file in files:
            commit_sha = self._upload_single_file(repo_name, file)
        
        if not commit_sha:
            raise Exception("No files were uploaded successfully")
            
        self.logger.info(f"All files uploaded successfully. Latest commit: {commit_sha}")
        return commit_sha
    
    def _upload_single_file(self, repo_name: str, file: CodeFile) -> str:
        """Upload a single file to GitHub"""
        content_encoded = base64.b64encode(file.content.encode()).decode()
        
        # Check if file exists
        get_response = requests.get(
            f"https://api.github.com/repos/{repo_name}/contents/{file.name}",
            headers=self.headers
        )
        
        payload = {
            "message": f"Add/Update {file.name}",
            "content": content_encoded
        }
        
        # If file exists, include the SHA for update
        if get_response.status_code == 200:
            payload["sha"] = get_response.json()["sha"]
        
        response = requests.put(
            f"https://api.github.com/repos/{repo_name}/contents/{file.name}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            self.logger.error(f"Failed to upload {file.name}: {response.json()}")
            raise Exception(f"Failed to upload {file.name}")
        
        return response.json()["commit"]["sha"]
    
    def enable_pages(self, repo_url: str) -> str:
        """Enable GitHub Pages for the repository and return the pages URL"""
        self.logger.info(f"Enabling GitHub Pages for repository: {repo_url}")
        
        repo_name = repo_url.split("github.com/")[-1]
        payload = {
            "source": {"branch": "main", "path": "/"}
        }
        
        response = requests.post(
            f"https://api.github.com/repos/{repo_name}/pages",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            # Check if pages is already enabled
            get_response = requests.get(
                f"https://api.github.com/repos/{repo_name}/pages",
                headers=self.headers
            )
            if get_response.status_code == 200:
                pages_url = get_response.json()["html_url"]
                self.logger.info(f"GitHub Pages already enabled: {pages_url}")
                return pages_url
            else:
                self.logger.error(f"Failed to enable GitHub Pages: {response.json()}")
                raise Exception("GitHub Pages enablement failed")
        
        pages_url = response.json()["html_url"]
        self.logger.info(f"GitHub Pages enabled successfully: {pages_url}")
        return pages_url