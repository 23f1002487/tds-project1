"""
AI service for code generation using Pydantic AI
"""
import logging
from typing import Dict, Optional, List
from ..Models.models import GeneratedCode, CodeFile, Attachment
from ..Config.config import config

try:
    from pydantic_ai import Agent # type: ignore
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    logging.warning("pydantic-ai not available, falling back to templates")


class AIService:
    """Service for AI-based code generation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._code_generator = None
        self._code_reviser = None
        
        if PYDANTIC_AI_AVAILABLE and config.has_ai_key:
            self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize Pydantic AI agents"""
        model_config = {}
        model_name = "unknown"
        
        try:
            # Get API token and URL (prioritize AIPIPE)
            api_token = config.get_ai_key
            base_url = config.get_ai_url
            
            if not api_token:
                self.logger.warning("No AIPIPE_TOKEN available")
                return
            
            # Determine model name based on service type
            if config.aipipe_token and config.aipipe_token.strip():
                # Using AIPIPE service - use direct model name
                model_name = 'gpt-4o-mini'  # Use a simpler, more reliable model
                self.logger.info(f"Using AIPIPE service with model: {model_name}")
            else:
                # Using OpenAI directly
                model_name = 'gpt-4o-mini'
                self.logger.info(f"Using OpenAI service with model: {model_name}")
            
            # Configure the model with appropriate settings
            if base_url and base_url != "https://api.openai.com/v1":
                model_config = {
                    'openai_base_url': base_url,
                    'openai_api_key': api_token
                }
                self.logger.info(f"Using custom AI URL: {base_url}")
            else:
                model_config = {
                    'openai_api_key': api_token
                }
                self.logger.info("Using default OpenAI URL")
            
            self._code_generator = Agent( #type: ignore
                model_name,
                result_type=GeneratedCode,
                system_prompt=self._get_generation_prompt(),
                **model_config
            )
            
            self._code_reviser = Agent( #type: ignore
                model_name,
                result_type=GeneratedCode,
                system_prompt=self._get_revision_prompt(),
                **model_config
            )
            self.logger.info("Pydantic AI agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI agents: {e}")
            self.logger.error(f"AIPIPE_TOKEN present: {bool(config.aipipe_token)}")
            self.logger.error(f"Model config: {model_config}")
            self.logger.error(f"Model name: {model_name}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            self._code_generator = None
            self._code_reviser = None
    
    def _get_generation_prompt(self) -> str:
        """Get system prompt for code generation"""
        return """You are an expert full-stack web developer. Generate complete, functional web applications based on task briefs.

CRITICAL REQUIREMENTS:
- Analyze the task brief carefully and understand exactly what needs to be built
- Create a fully working application that meets ALL requirements specified in the task brief
- Generate clean, well-commented, production-ready code
- Include proper error handling and user feedback
- Make the UI responsive and user-friendly
- Ensure all functionality described in the task is implemented and working
- Do NOT make assumptions about what the task is - build exactly what is requested

RESPONSE FORMAT:
Your response must be a JSON object with these exact keys:
- "index_html": Complete HTML file with proper structure, meta tags, and all required elements
- "style_css": Complete CSS file with styling, responsive design, and visual appeal  
- "script_js": Complete JavaScript file with all functionality described in the task brief
- "readme_md": Comprehensive documentation explaining the application, how to use it, and any special features

Each file should be complete, functional, and directly address the requirements in the task brief."""
    
    def _get_revision_prompt(self) -> str:
        """Get system prompt for code revision"""
        return """You are an expert developer making revisions to existing web applications based on feedback.

REQUIREMENTS:
- Carefully analyze the feedback and current implementation
- Make appropriate improvements while maintaining core functionality
- Address specific concerns and enhancement requests
- Improve code quality, user experience, and functionality
- Ensure all changes are backwards compatible unless specifically requested otherwise
- Focus on the specific issues mentioned in the feedback

RESPONSE FORMAT:
Your response must be a JSON object with these exact keys:
- "index_html": Updated HTML file with improvements
- "style_css": Updated CSS file with better styling
- "script_js": Updated JavaScript file with enhanced functionality
- "readme_md": Updated documentation reflecting the improvements

Ensure all files work together cohesively and address the feedback provided."""
    
    def generate_code(self, task_brief: str, round_num: int = 1, existing_files: Optional[Dict] = None) -> Dict[str, str]:
        """Generate code using AI or fallback templates"""
        try:
            if self._can_use_ai():
                return self._generate_with_ai(task_brief, round_num, existing_files)
            else:
                self.logger.info("Using fallback template generation")
                return self._generate_with_template(task_brief)
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return self._generate_with_template(task_brief)
    
    def _can_use_ai(self) -> bool:
        """Check if AI generation is available"""
        return (PYDANTIC_AI_AVAILABLE and 
                config.has_ai_key and 
                self._code_generator is not None)
    
    def _generate_with_ai(self, task_brief: str, round_num: int, existing_files: Optional[Dict]) -> Dict[str, str]:
        """Generate code using Pydantic AI"""
        if round_num == 1:
            user_prompt = f"""TASK BRIEF TO IMPLEMENT:
{task_brief}

Generate a complete web application that fulfills this exact task. Read the task brief carefully and implement every requirement specified. Do not add unrelated features or assume what the task might be about - build exactly what is described in the task brief."""
            
            result = self._code_generator.run_sync(user_prompt) #type: ignore
        else:
            import json
            user_prompt = f"""REVISION REQUEST:
Original Task: {task_brief}

Current Implementation:
{json.dumps(existing_files or {}, indent=2)}

Please revise the application based on feedback and improve it significantly. Address any issues or enhancement requests while maintaining the core functionality."""
            
            result = self._code_reviser.run_sync(user_prompt) #type: ignore
        
        return {
            "index.html": result.data.index_html,
            "style.css": result.data.style_css,
            "script.js": result.data.script_js,
            "README.md": result.data.readme_md
        }
    
    def _generate_with_template(self, task_brief: str) -> Dict[str, str]:
        """Generate code using adaptive templates"""
        from templates import TemplateGenerator #type: ignore
        generator = TemplateGenerator()
        return generator.generate_adaptive_template(task_brief)


class TemplateGenerator:
    """Fallback template generator"""
    
    def generate_adaptive_template(self, task_brief: str) -> Dict[str, str]:
        """Generate a basic adaptive template based on the task brief"""
        task_name = self._extract_task_name(task_brief)
        
        return {
            "index.html": self._generate_html(task_name, task_brief),
            "style.css": self._generate_css(),
            "script.js": self._generate_js(task_brief),
            "README.md": self._generate_readme(task_name, task_brief)
        }
    
    def _extract_task_name(self, task_brief: str) -> str:
        """Extract a suitable task name from the brief"""
        words = task_brief.split()[:3]
        return " ".join(word.strip(".,!?") for word in words if word.isalpha())
    
    def _generate_html(self, task_name: str, task_brief: str) -> str:
        """Generate adaptive HTML template"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{task_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>{task_name}</h1>
        <div class="app-section">
            <div class="description">
                <p>{task_brief}</p>
            </div>
            <div class="main-functionality">
                <div class="input-section">
                    <input type="text" id="main-input" placeholder="Enter input here">
                    <button onclick="processInput()">Process</button>
                </div>
                <div class="output-section">
                    <div id="output" class="output"></div>
                </div>
            </div>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
    
    def _generate_css(self) -> str:
        """Generate adaptive CSS template"""
        return '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    background: white;
    border-radius: 10px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    max-width: 800px;
    width: 90%;
}

h1 {
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
}

.app-section {
    margin-bottom: 1.5rem;
}

.description {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 5px;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
}

.input-section {
    margin-bottom: 1rem;
}

input[type="text"], input[type="url"] {
    width: 70%;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 5px;
    margin-right: 10px;
    font-size: 1rem;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s;
}

button:hover:not(:disabled) {
    background: #5a6fd8;
}

.output {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 1rem;
    min-height: 100px;
    white-space: pre-wrap;
}

.output.success {
    background: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}

.output.error {
    background: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}'''
    
    def _generate_js(self, task_brief: str) -> str:
        """Generate adaptive JavaScript template"""
        task_name = self._extract_task_name(task_brief)
        return f'''// {task_name} Application
// Task: {task_brief}

function processInput() {{
    const input = document.getElementById('main-input').value;
    const output = document.getElementById('output');
    
    if (!input.trim()) {{
        output.textContent = 'Please enter some input';
        output.className = 'output error';
        return;
    }}
    
    try {{
        const result = performTaskSpecificProcessing(input);
        output.textContent = result;
        output.className = 'output success';
    }} catch (error) {{
        output.textContent = 'Error processing input: ' + error.message;
        output.className = 'output error';
    }}
}}

function performTaskSpecificProcessing(input) {{
    // This function should be customized based on the specific task
    return `Processed: ${{input}} - Task completed successfully!`;
}}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {{
    console.log('Application initialized');
    
    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const inputParam = urlParams.get('input') || urlParams.get('url');
    if (inputParam) {{
        document.getElementById('main-input').value = inputParam;
    }}
}});'''
    
    def _generate_readme(self, task_name: str, task_brief: str) -> str:
        """Generate adaptive README template"""
        return f'''# {task_name}

## Description
{task_brief}

## Features
- Responsive web interface
- Input processing functionality
- Error handling and user feedback
- URL parameter support

## Usage
1. Open the application in a web browser
2. Enter your input in the text field
3. Click "Process" to execute the main functionality
4. View the results in the output section

## File Structure
- `index.html` - Main application interface
- `style.css` - Styling and responsive design
- `script.js` - Application logic and functionality
- `README.md` - This documentation

## Technical Details
This application is built with vanilla HTML, CSS, and JavaScript for maximum compatibility and performance.
'''