# Student API Configuration and Setup Guide

## Environment Setup

### Required Environment Variables
Before running the application, you need to set up the following environment variables:

```bash
export secret="**********"  # Your secret key (replace with your actual secret)
export github_token="***********"  # Your GitHub PAT

# AIPIPE Configuration (Recommended)
export AIPIPE_TOKEN="**********"  # AIPIPE API token
export AIPIPE_URL="https://aipipe.org/openrouter/v1"  # AIPIPE URL (optional, defaults to openrouter)
# Alternative: export AIPIPE_URL="https://aipipe.org/openai/v1"  # For direct OpenAI via AIPIPE

# Legacy OpenAI Configuration (Optional - for backward compatibility)
export OPENAI_API_KEY="your_openai_api_key"  # Direct OpenAI API key (optional)
export OPENAI_URL="https://api.openai.com/v1"  # OpenAI API URL (optional, defaults to standard URL)
```

**Note**: The system prioritizes AIPIPE configuration over direct OpenAI. If `AIPIPE_TOKEN` is set, it will use AIPIPE service with the model format `openai/gpt-4.1-nano`. Otherwise, it falls back to direct OpenAI with model format `openai:gpt-4.1-nano`.

### GitHub Personal Access Token Setup
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with the following permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:repo_hook` (Admin repository hooks)

## Running the Application

### 1. Install Dependencies
The application uses uv for dependency management. If you don't have uv installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### 2. Run the API Server
```bash
# Using uv (recommended)
uv run main.py

# Or using python directly
python main.py
```

The server will start on `http://localhost:8000`

### 3. Test the API
```bash
# Run all tests
python test_workflow.py

# Run specific tests
python test_workflow.py health    # Test server health
python test_workflow.py round1    # Test round 1 submission
python test_workflow.py round2    # Test round 2 submission
```

## API Endpoints

### GET /
Health check endpoint
Returns: `{"message": "Hello, Welcome to the Task Submission API"}`

### POST /api-endpoint
Main task submission endpoint

**Request Body:**
```json
{
  "email": "student@example.com",
  "secret": "your_secret_key",
  "task": "task-name",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Task description",
  "checks": ["Check 1", "Check 2"],
  "evaluation_url": "https://example.com/notify",
  "attachments": [{"name": "file.txt", "url": "data:..."}]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task received successfully"
}
```

## Workflow

### Round 1 (Initial Build)
1. Receive task request
2. Validate secret key
3. Generate application code (HTML, CSS, JS, README.md)
4. Create GitHub repository
5. Upload files to repository
6. Enable GitHub Pages
7. Send results to evaluation URL

### Round 2 (Revisions)
1. Receive revision request
2. Validate secret key
3. Find existing repository
4. Generate updated code based on new requirements
5. Update repository files
6. Send results to evaluation URL

## Generated Application Structure
```
repository/
├── index.html      # Main application page
├── style.css       # Styling
├── script.js       # Application logic
├── README.md       # Documentation
└── LICENSE         # MIT License (auto-generated)
```

## Configuration

The application supports the following environment variables:

### Required Variables
- `secret`: Authentication secret key for API access
- `github_token`: GitHub Personal Access Token with repository permissions

### AI Configuration Variables (Priority Order)
1. **AIPIPE Configuration (Recommended)**
   - `AIPIPE_TOKEN`: AIPIPE API token for AI-powered code generation
   - `AIPIPE_URL`: AIPIPE service URL (defaults to "https://aipipe.org/openrouter/v1")
     - Alternative: "https://aipipe.org/openai/v1" for direct OpenAI via AIPIPE

2. **Direct OpenAI Configuration (Fallback)**
   - `OPENAI_API_KEY`: Direct OpenAI API key for AI-powered code generation
   - `OPENAI_URL`: Custom OpenAI API URL (defaults to "https://api.openai.com/v1")

### Optional Variables
- `LOG_FILE`: Log file path (defaults to "task_log.txt")
- `LOG_LEVEL`: Logging level (defaults to "INFO")

### AI Service Selection
The application automatically selects the AI service based on available configuration:
1. **AIPIPE Service**: If `AIPIPE_TOKEN` is set, uses AIPIPE with model format `openai/gpt-4.1-nano`
2. **Direct OpenAI**: If only OpenAI credentials are set, uses OpenAI with model format `openai:gpt-4.1-nano`
3. **Template Fallback**: If no AI keys are provided, uses static templates

## Logging
All operations are logged to `task_log.txt` with timestamps and detailed information.

## Error Handling
- Invalid secret: Returns 403 Forbidden
- Invalid payload: Returns 422 Validation Error
- GitHub API errors: Logged and handled gracefully
- Evaluation URL submission: Retries with exponential backoff (1, 2, 4, 8, 16 seconds)

## Security Notes
- Never commit your GitHub token to version control
- Use environment variables for sensitive data
- The secret key is validated on every request
- All operations are logged for audit purposes

## Troubleshooting

### Common Issues
1. **"Failed to create GitHub repository"**
   - Check your GitHub token permissions
   - Ensure the token hasn't expired
   - Verify repository name doesn't already exist

2. **"GitHub Pages enablement failed"**
   - Repository must be public
   - Ensure GitHub token has workflow permissions
   - Check if Pages is already enabled

3. **"Connection refused"**
   - Ensure the API server is running
   - Check port 8000 is not in use by another application
   - Verify firewall settings

### Debug Mode
To enable verbose logging, modify the logging configuration in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```