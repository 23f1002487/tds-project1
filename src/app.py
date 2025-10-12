"""
Main FastAPI application for the Student Task Processor.

This application provides a web API for processing student tasks including:
- Code generation using AI services
- GitHub repository creation and management
- File upload and GitHub Pages deployment
- Task validation and processing workflow

The application expects specific environment variables:
- secret: Secret key for authentication
- github_token: GitHub personal access token
- OPENAI_API_KEY: OpenAI/AIPIPE API key
- OPENAI_BASE_URL: API base URL (optional, defaults to AIPIPE)
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#           "fastapi[standard]", 
#           "uvicorn", 
#           "pydantic",
#           "pydantic-ai",
#           "httpx", 
#           "requests",
#           "logging"
#          ]
# ///

import logging
import os
from fastapi import FastAPI, HTTPException #type: ignore
from .Models.models import TaskRequest, TaskResponse
from .services.task_service import TaskProcessor
from .Config.config import config

# Configure logging with robust error handling
import os
try:
    # Try to create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.log_file) or "/tmp"
    os.makedirs(log_dir, exist_ok=True)
    
    # Try to use the configured log file, fall back to console if permission denied
    log_file = config.log_file if os.access(os.path.dirname(config.log_file) or ".", os.W_OK) else None
    
    logging.basicConfig(
        filename=log_file,
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        force=True
    )
        
except Exception as e:
    # Fall back to console logging if anything goes wrong
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        force=True
    )
    logging.warning(f"Logging setup failed, using console: {e}")

# Initialize FastAPI application and services
app = FastAPI(
    title="Student Task Processor", 
    version="1.0.0",
    description="AI-powered web application generator for student tasks"
)
task_processor = TaskProcessor()


@app.post("/process_task")
async def process_task(task_request: TaskRequest) -> TaskResponse:
    """
    Process a student task request through the complete workflow.
    
    This endpoint handles:
    1. Authentication and validation
    2. AI-powered code generation
    3. GitHub repository creation
    4. File upload and GitHub Pages deployment
    5. Evaluation URL submission
    
    Args:
        task_request: TaskRequest containing task details, authentication, and requirements
        
    Returns:
        TaskResponse with repository URL, commit SHA, and GitHub Pages URL
        
    Raises:
        HTTPException: 403 for authentication errors, 500 for processing errors
    """
    try:
        return await task_processor.process_task(task_request)
    except ValueError as e:
        logging.warning(f"Validation error: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logging.error(f"Task processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        dict: Health status including AI availability, GitHub configuration,
              and overall system health
    """
    return {
        "status": "healthy",
        "ai_available": task_processor.ai_service._can_use_ai(),
        "github_configured": bool(config.github_token != "..."),
        "config_loaded": True
    }

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    Returns:
        dict: API metadata and endpoint documentation
    """
    return {
        "message": "Student Task Processor API",
        "version": "1.0.0",
        "description": "AI-powered web application generator for educational tasks",
        "endpoints": {
            "process_task": "POST /process_task - Process student task requests",
            "health": "GET /health - Check service health status"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)