# Logs Directory

This directory contains application log files for the Student Task Processor.

## Log Files:
- `task_log.txt` - Main application log with detailed DEBUG information
- Contains timestamps, function names, line numbers, and detailed error tracking

## Log Format:
```
YYYY-MM-DD HH:MM:SS [LEVEL] module:line - function() - message
```

Example:
```
2025-10-15 14:30:45 [   DEBUG] src.app:125 - health_check() - Health endpoint called
2025-10-15 14:30:45 [    INFO] src.services.task_service:45 - process_task() - Task processing started
```

## Access Methods:
1. **Files Tab**: Access via Hugging Face Spaces Files interface
2. **API Endpoint**: `GET /logs?lines=50` for recent entries
3. **Direct File**: Download `logs/task_log.txt` from repository

This directory is persistent and will be visible in Hugging Face Spaces Files tab.