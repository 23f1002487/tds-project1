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
    # Ensure log file is in the root directory (accessible via HF Files tab)
    log_file_path = config.log_file
    if not os.path.isabs(log_file_path):
        # Make sure it's in the current working directory (root of HF Space)
        log_file_path = os.path.join(os.getcwd(), config.log_file)
    
    # Create log directory if needed
    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure file logging
    logging.basicConfig(
        filename=log_file_path,
        level=getattr(logging, config.log_level),
        format="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True
    )
    
    # Also add console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s", 
                         "%Y-%m-%d %H:%M:%S")
    )
    logging.getLogger().addHandler(console_handler)
    
    # Write initial log entry to ensure file is created
    logging.info(f"Logging initialized - file: {log_file_path}")
        
except Exception as e:
    # Fall back to console logging if anything goes wrong
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.DEBUG),
        format="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
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

# Log application startup
logging.info("="*50)
logging.info("Student Task Processor API starting up")
logging.info(f"Python working directory: {os.getcwd()}")
logging.info(f"Log level: {config.log_level}")
logging.info(f"Log file: {config.log_file}")
logging.info(f"Log file absolute path: {os.path.abspath(config.log_file)}")
logging.info(f"Log file exists: {os.path.exists(config.log_file)}")
logging.info("Available endpoints: /process_task, /health, /, /logs")
logging.info("📁 Log file accessible via HF Spaces Files tab")
logging.info("="*50)


@app.post("/process_task")
async def process_task(task_request: TaskRequest) -> dict:
    """
    Process a student task request with immediate response and background processing.
    
    This endpoint provides immediate response while processing the task in the background:
    1. Authentication and validation (immediate)
    2. Immediate 200 response with processing status
    3. Background AI-powered code generation
    4. Background GitHub repository creation and deployment
    5. Background evaluation URL submission with complete results
    
    Args:
        task_request: TaskRequest containing task details, authentication, and requirements
        
    Returns:
        dict: Immediate response with processing status, tracking ID, and estimated completion time
        
    Raises:
        HTTPException: 403 for authentication errors, 500 for processing errors
        
    Note:
        The actual task processing happens in the background. Complete results
        will be submitted to the provided evaluation_url when processing finishes.
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
    logging.debug("Health endpoint called")
    try:
        ai_available = task_processor.ai_service._can_use_ai()
        logging.debug(f"AI availability check result: {ai_available}")
    except Exception as e:
        logging.warning(f"Error checking AI availability: {e}")
        ai_available = False
        
    health_status = {
        "status": "healthy",
        "ai_available": ai_available,
        "github_configured": bool(config.github_token != "..."),
        "config_loaded": True
    }
    logging.debug(f"Health check response: {health_status}")
    return health_status

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    Returns:
        dict: API metadata and endpoint documentation
    """
    logging.debug("Root endpoint called")
    response = {
        "message": "Student Task Processor API",
        "version": "1.0.0",
        "description": "AI-powered web application generator for educational tasks",
        "endpoints": {
            "process_task": "POST /process_task - Process student task requests",
            "health": "GET /health - Check service health status"
        },
        "documentation": "/docs"
    }
    logging.debug(f"Root endpoint response: {response}")
    return response


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)