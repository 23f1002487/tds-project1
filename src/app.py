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
from fastapi import FastAPI, HTTPException #type: ignore
from .Models.models import TaskRequest, TaskResponse
from .services.task_service import TaskProcessor
from .Config.config import config

# Configure logging
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
    
    # If we couldn't write to file, also log to console
    if log_file is None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.log_level))
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        logging.warning("Could not write to log file, using console logging")
        
except Exception as e:
    # Fall back to console logging if anything goes wrong
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        force=True
    )
    logging.warning(f"Logging setup failed, using console: {e}")

app = FastAPI(title="Student Task Processor", version="1.0.0")
task_processor = TaskProcessor()


@app.post("/process_task")
async def process_task(task_request: TaskRequest) -> TaskResponse:
    """
    Process a task request and return the completed response
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_available": task_processor.ai_service._can_use_ai(),
        "github_configured": bool(config.github_token != "..."),
        "config_loaded": True
    }


@app.get("/debug")
async def debug_config():
    """Debug endpoint to check configuration (remove in production)"""
    try:
        from pydantic_ai import Agent
        pydantic_ai_import_ok = True
        agent_test_error = None
        
        # Try to create a simple agent
        try:
            test_agent = Agent('gpt-4o-mini', openai_api_key=config.get_ai_key, openai_base_url=config.get_ai_url)
            agent_creation_ok = True
        except Exception as e:
            agent_creation_ok = False
            agent_test_error = str(e)
            
    except ImportError as e:
        pydantic_ai_import_ok = False
        agent_creation_ok = False
        agent_test_error = f"Import error: {str(e)}"
    
    return {
        "pydantic_ai_import": pydantic_ai_import_ok,
        "agent_creation": agent_creation_ok,
        "agent_error": agent_test_error,
        "pydantic_ai_available": hasattr(task_processor.ai_service, '_code_generator') and task_processor.ai_service._code_generator is not None,
        "has_aipipe_token": bool(config.aipipe_token and config.aipipe_token.strip() and config.aipipe_token != "..."),
        "has_openai_key": bool(config.openai_api_key and config.openai_api_key.strip() and config.openai_api_key != "..."),
        "has_ai_key": config.has_ai_key,
        "ai_key_length": len(config.get_ai_key or "") if config.get_ai_key else 0,
        "aipipe_url": config.aipipe_url,
        "openai_url": config.openai_url,
        "secret_configured": bool(config.secret_key != "..."),
        "github_configured": bool(config.github_token != "...")
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Student Task Processor API",
        "version": "1.0.0",
        "endpoints": {
            "process_task": "POST /process_task",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)