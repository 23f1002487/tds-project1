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
from Models.models import TaskRequest, TaskResponse
from services.task_service import TaskProcessor
from Config.config import config

# Configure logging
logging.basicConfig(
    filename=config.log_file,
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)

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