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
    # Try multiple writable locations for HF Spaces (prioritize persistent workspace)
    possible_log_locations = [
        "/app/logs/task_log.txt",  # HF Spaces persistent workspace
        "./logs/task_log.txt",  # Local logs directory (persistent)
        "/app/task_log.txt",  # Root of HF workspace
        "task_log.txt",  # Current directory
        config.log_file,  # Original location
        "/tmp/task_log.txt",  # /tmp as last resort (not visible in Files tab)
    ]
    
    log_file_path = None
    for log_path in possible_log_locations:
        try:
            # Create directory if needed
            log_dir = os.path.dirname(log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                print(f"📁 Created/verified directory: {log_dir}")
            
            # Test if we can write to this location
            test_dir = os.path.dirname(log_path) if os.path.dirname(log_path) else "."
            if os.access(test_dir, os.W_OK):
                log_file_path = log_path
                print(f"✅ Selected log location: {log_file_path}")
                break
            else:
                print(f"❌ No write access: {log_path}")
        except Exception as e:
            print(f"❌ Failed to access {log_path}: {e}")
            continue
    
    if log_file_path:
        # Configure file logging
        logging.basicConfig(
            filename=log_file_path,
            level=getattr(logging, config.log_level),
            format="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True
        )
        print(f"✅ Logging to file: {log_file_path}")
    else:
        # No writable location found, use console only
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True
        )
        print("⚠️  No writable log location found, using console only")
    
    # Also add console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s", 
                         "%Y-%m-%d %H:%M:%S")
    )
    logging.getLogger().addHandler(console_handler)
    
    # Write initial log entry
    logging.info(f"Logging initialized - file: {log_file_path or 'console only'}")
        
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
logging.info(f"Configured log file: {config.log_file}")
logging.info(f"User ID: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
logging.info(f"Writable directories priority: /app/logs, ./logs, /app, current dir, /tmp")
logging.info("Available endpoints: /process_task, /health, /, /logs")
logging.info("📁 Log file in persistent workspace will be visible in HF Files tab")
logging.info("="*50)


@app.get("/process_task")
async def process_task_get():
    """
    GET request handler for /process_task - provides helpful error message.
    
    This endpoint only accepts POST requests. This handler helps users who
    accidentally use GET instead of POST.
    """
    return {
        "error": "Method Not Allowed",
        "message": "This endpoint only accepts POST requests",
        "correct_usage": {
            "method": "POST",
            "url": "/process_task",
            "content_type": "application/json",
            "required_fields": [
                "email", "secret", "task", "round", "nonce", 
                "brief", "checks", "evaluation_url"
            ]
        },
        "documentation": "/docs"
    }


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
            "health": "GET /health - Check service health status",
            "logs": "GET /logs?lines=50 - Get recent application logs"
        },
        "documentation": "/docs"
    }
    logging.debug(f"Root endpoint response: {response}")
    return response


@app.get("/logs")
async def get_logs(lines: int = 50):
    """
    Get recent application logs for debugging.
    
    Args:
        lines: Number of recent log lines to return (default: 50, max: 200)
        
    Returns:
        dict: Recent log entries and file information
    """
    logging.debug(f"Logs endpoint called, requesting {lines} lines")
    
    try:
        lines = min(lines, 200)  # Limit to prevent abuse
        
        # Try to find log file in possible locations (prioritize persistent workspace)
        possible_locations = [
            "/app/logs/task_log.txt",  # HF Spaces persistent workspace logs
            "./logs/task_log.txt",     # Local logs directory
            "/app/task_log.txt",       # Root of HF workspace
            "task_log.txt",            # Current directory
            config.log_file,           # Original config location
            "/tmp/task_log.txt",       # Temporary location (last resort)
        ]
        
        found_log = None
        for log_path in possible_locations:
            if os.path.exists(log_path):
                found_log = log_path
                break
        
        if found_log:
            with open(found_log, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            return {
                "status": "success",
                "log_file": found_log,
                "total_lines": len(all_lines),
                "returned_lines": len(recent_lines),
                "logs": [line.strip() for line in recent_lines]
            }
        else:
            return {
                "status": "no_file",
                "message": "No log file found - console logging only",
                "searched_locations": possible_locations,
                "note": "Check HF Spaces Logs tab for console output"
            }
            
    except Exception as e:
        logging.error(f"Error reading logs: {e}")
        return {
            "status": "error", 
            "message": f"Error reading logs: {str(e)}",
            "note": "Check HF Spaces Logs tab for console output"
        }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)