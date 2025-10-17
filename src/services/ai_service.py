"""
AI service for code generation using Pydantic AI.

This service provides AI-powered code generation capabilities for web applications.
It handles both initial code generation (Round 1) and code revision (Round 2+).

Key features:
- Integration with pydantic-ai for structured code generation
- Support for multiple AI models via AIPIPE/OpenRouter
- Proper JSON parsing and validation
- Seed placeholder processing for evaluation framework compatibility
- Comprehensive error handling and fallback mechanisms

Environment variables required:
- OPENAI_API_KEY: API key for AI service
- OPENAI_BASE_URL: Base URL for AI service (optional, defaults to AIPIPE)
"""
import logging
from typing import Dict, Optional, List
from ..Models.models import GeneratedCode, CodeFile, Attachment
from ..Config.config import config

try:
    from pydantic_ai import Agent
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
        
        # Try to initialize agents
        self._try_initialize_agents()
    
    def _try_initialize_agents(self):
        """Try to initialize agents, with retry capability"""
        if PYDANTIC_AI_AVAILABLE:
            self._initialize_agents()
    
    def ensure_agents_initialized(self):
        """Ensure agents are initialized - call this when you need AI functionality"""
        if self._code_generator is None and PYDANTIC_AI_AVAILABLE:
            self.logger.info("Attempting to initialize AI agents on demand")
            self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize Pydantic AI agents"""
        model_name = "gpt-4.1-nano"  # Default model
        
        try:            
            # Check if we have AIPIPE_TOKEN from config
            if config.openai_token and config.openai_token.strip():
                openai_token = config.openai_token
                aipipe_base_url = config.aipipe_url or "https://aipipe.org/openrouter/v1"
                
                self.logger.info(f"  - Base URL: {aipipe_base_url}")
                self.logger.info(f"  - Model: {model_name}")
                print(f"After logging AIPIPE configuration {aipipe_base_url} and {model_name}")
                              
            else:
                self.logger.warning("No API token available, cannot initialize AI agents")
                return
            
            # Create agents without passing any parameters (they use environment variables)
            self._code_generator = Agent(
                model_name,
                system_prompt=self._get_generation_prompt()
            )
            
            self._code_reviser = Agent(
                model_name,
                system_prompt=self._get_revision_prompt()
            )
            self.logger.info("Pydantic AI agents initialized successfully")
            print("Pydantic AI agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI agents: {e}")
            self.logger.error(f"AIPIPE_TOKEN present: {bool(config.openai_token)}")
            self.logger.error(f"Model name: {model_name}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            print(f"Failed to initialize AI agents: {e}")
            self._code_generator = None
            self._code_reviser = None
    
    def _get_generation_prompt(self) -> str:
        """Get system prompt for code generation"""
        print("Getting generation prompt")
        return """You are an expert full-stack web developer. Generate complete, functional web applications based on task briefs.

CRITICAL REQUIREMENTS:
- Analyze the task brief carefully and understand exactly what needs to be built
- Create a fully working application that meets ALL requirements specified in the task brief
- Generate clean, well-commented, production-ready code
- Include proper error handling and user feedback
- Make the UI responsive and user-friendly
- Ensure all functionality described in the task is implemented and working
- Do NOT make assumptions about what the task is - build exactly what is requested
- Pay special attention to the validation checks - every check must be satisfied in your implementation

SPECIAL HANDLING FOR EVALUATION CHECKS:
- If checks start with "js:", these are JavaScript validation expressions that will be executed in the browser
- Ensure your HTML elements have the exact IDs, classes, and attributes needed for these checks to pass
- For "js:" checks, make sure the DOM elements and JavaScript functionality exists as expected
- Handle ${seed} placeholders in task briefs by replacing them with appropriate values

ATTACHMENT HANDLING:
- If attachments are provided, process them according to the task requirements
- Base64 encoded files should be decoded and used as specified in the brief
- Create appropriate file handling and display functionality

IMPLEMENTATION GUIDELINES:
- If the task requires interactive elements (buttons, forms, etc.), implement them properly
- If the task requires calculations, implement the actual calculation logic
- If the task requires data processing, implement the processing functions
- If the task requires visual elements, style them appropriately
- Always implement the EXACT functionality described, not a simplified version
- Use semantic HTML with proper IDs and classes for automated testing
- Ensure JavaScript functionality is robust and handles edge cases

RESPONSE FORMAT:
Your response must be a JSON object with these exact keys:
- "index_html": Complete HTML file with proper structure, meta tags, and all required elements
- "style_css": Complete CSS file with styling, responsive design, and visual appeal  
- "script_js": Complete JavaScript file with all functionality described in the task brief
- "readme_md": Comprehensive documentation explaining the application, how to use it, and any special features

CRITICAL: Return ONLY valid JSON. Use proper JSON string escaping for newlines and quotes. Do NOT use template literals (backticks). Do NOT include any markdown code blocks or extra text outside the JSON.

Each file should be complete, functional, and directly address the requirements in the task brief."""
    
    def _get_revision_prompt(self) -> str:
        """Get system prompt for code revision"""
        return """You are an expert full-stack web developer specializing in improving and refining web applications based on feedback and evaluation results.

CRITICAL REQUIREMENTS:
- Analyze the current implementation and feedback carefully
- Make targeted improvements while preserving working functionality
- Address specific issues, bugs, or enhancement requests mentioned in feedback
- Improve code quality, user experience, accessibility, and performance
- Ensure all validation checks continue to pass after improvements
- Add new features or functionality if requested in feedback
- Fix any bugs or issues identified in the evaluation
- Enhance styling, responsiveness, and overall polish

REVISION PRINCIPLES:
- Maintain backwards compatibility unless explicitly asked to change core behavior
- Improve error handling and edge case management
- Enhance user interface and user experience
- Add proper form validation and input sanitization
- Improve accessibility (ARIA labels, keyboard navigation, etc.)
- Optimize performance and code organization
- Add helpful user feedback and status messages
- Ensure cross-browser compatibility

SPECIAL HANDLING FOR EVALUATION FEEDBACK:
- If feedback mentions failed validation checks, ensure those checks pass in the revised version
- If "js:" checks are mentioned, pay special attention to JavaScript functionality and DOM structure
- If UI/UX issues are noted, focus on improving the visual design and user interaction
- If performance issues are mentioned, optimize code and reduce unnecessary operations
- If accessibility concerns are raised, add proper ARIA attributes and keyboard support

RESPONSE FORMAT:
Your response must be a JSON object with these exact keys:
- "index_html": Updated HTML file with improvements and fixes
- "style_css": Updated CSS file with better styling, responsiveness, and visual enhancements
- "script_js": Updated JavaScript file with enhanced functionality, better error handling, and performance improvements
- "readme_md": Updated documentation reflecting all improvements, new features, and usage instructions

CRITICAL: Return ONLY valid JSON. Use proper JSON string escaping for newlines and quotes. Do NOT use template literals (backticks). Do NOT include any markdown code blocks or extra text outside the JSON."""
    
    async def generate_code(self, task_brief: str, round_num: int = 1, existing_files: Optional[Dict] = None, checks: Optional[list] = None, attachments: Optional[list] = None, email: Optional[str] = None) -> Dict[str, str]:
        """Generate code using AI or fallback templates"""
        try:
            if self._can_use_ai():
                return await self._generate_with_ai(task_brief, round_num, existing_files, checks, attachments, email)
            else:
                self.logger.error("AI service not available and no fallback - cannot generate code")
                raise Exception("AI service not available - pydantic-ai not installed or configured")
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise Exception(f"Code generation failed: {e}")
    
    def _can_use_ai(self) -> bool:
        """Check if AI generation is available"""
        # Try to initialize if not already done
        if self._code_generator is None:
            print("Attempting to initialize AI agents... code_generator is None")
            self.ensure_agents_initialized()
            
        return (PYDANTIC_AI_AVAILABLE and
                self._code_generator is not None)
    
    def _process_seed_placeholders(self, text: str, email: Optional[str] = None) -> str:
        """Process ${seed} placeholders in text"""
        if not text or "${seed}" not in text:
            return text
            
        # Generate a consistent seed based on email
        seed = "default"
        if email:
            # Extract the numeric part from email for seed
            import re
            match = re.search(r'(\d+)', email)
            if match:
                seed = match.group(1)[:6]  # Use first 6 digits
        
        return text.replace("${seed}", seed)
    
    def _extract_json_fields_manually(self, text: str) -> Optional[Dict[str, str]]:
        """
        Manually extract JSON fields when standard parsing fails.
        This is a fallback for malformed JSON from AI responses.
        """
        import re
        try:
            result = {}
            
            # Extract each field using regex patterns
            # Pattern: "field_name": "content..." (handles multiline)
            fields = ['index_html', 'style_css', 'script_js', 'readme_md']
            
            for field in fields:
                # Find the field and extract its value
                # Pattern matches: "field": "value" or "field": "multiline\nvalue"
                pattern = rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)(?<!\\)"'
                match = re.search(pattern, text, re.DOTALL)
                
                if match:
                    # Get the matched content and unescape it
                    content = match.group(1)
                    # Unescape JSON escape sequences
                    content = content.replace('\\n', '\n')
                    content = content.replace('\\t', '\t')
                    content = content.replace('\\"', '"')
                    content = content.replace('\\\\', '\\')
                    result[field] = content
                else:
                    self.logger.warning(f"Could not extract field: {field}")
                    result[field] = ""
            
            # Only return if we got at least index_html
            if result.get('index_html'):
                self.logger.info("Successfully extracted fields manually")
                return result
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Manual extraction failed: {e}")
            return None
    
    async def _generate_with_ai(self, task_brief: str, round_num: int, existing_files: Optional[Dict], checks: Optional[list] = None, attachments: Optional[list] = None, email: Optional[str] = None) -> Dict[str, str]:
        """Generate code using Pydantic AI"""
        if round_num == 1:
            # Process task brief for seed placeholders
            processed_brief = self._process_seed_placeholders(task_brief, email)
            
            # Build the prompt with checks if available
            checks_text = ""
            if checks:
                # Process checks for seed placeholders too
                processed_checks = [self._process_seed_placeholders(check, email) for check in checks]
                checks_list = "\n".join([f"- {check}" for check in processed_checks])
                checks_text = f"""

CRITICAL VALIDATION REQUIREMENTS - Your implementation MUST satisfy ALL of these checks:
{checks_list}

IMPORTANT: 
- For checks starting with "js:", these are JavaScript expressions that will be executed in the browser to validate your implementation
- Ensure your HTML elements have the exact IDs, classes, and attributes needed for these checks to pass
- Each check must be verifiable in the final application"""

            # Build attachments text if available
            attachments_text = ""
            if attachments:
                attachments_info = []
                for attachment in attachments:
                    name = attachment.get('name', 'unknown')
                    url = attachment.get('url', '')
                    if url.startswith('data:'):
                        # Extract content type and data
                        if 'base64,' in url:
                            content_type = url.split(';')[0].replace('data:', '')
                            attachments_info.append(f"- {name} ({content_type}): Base64 encoded content provided")
                        else:
                            attachments_info.append(f"- {name}: Data URL provided")
                    else:
                        attachments_info.append(f"- {name}: {url}")
                
                attachments_text = f"""

ATTACHMENTS PROVIDED:
{chr(10).join(attachments_info)}

IMPORTANT: Process these attachments according to the task requirements. Decode base64 content and use it as specified."""

            user_prompt = f"""TASK BRIEF TO IMPLEMENT:
{processed_brief}{checks_text}{attachments_text}

Generate a complete web application that fulfills this exact task. Read the task brief carefully and implement every requirement specified. Do not add unrelated features or assume what the task might be about - build exactly what is described in the task brief.

IMPLEMENTATION REQUIREMENTS:
1. Ensure ALL functionality described in the task brief is working
2. Validate that every check requirement is met in your implementation (especially "js:" checks)
3. Include proper event handlers and interactive elements with correct IDs and classes
4. Process any provided attachments according to the task requirements
5. Test all buttons, inputs, and user interactions
6. Make sure the application actually works as specified and passes all validation checks

IMPORTANT: Your response must be valid JSON only. Use this exact format:
{{"index_html": "<!DOCTYPE html>...", "style_css": "body {{...", "script_js": "// code here", "readme_md": "# title"}}

Make sure to properly escape all quotes and newlines in the JSON strings. Do not use backticks or template literals."""
            
            result = await self._code_generator.run(user_prompt) #type: ignore
        else:
            # Round 2 - Revision mode
            import json
            
            # Process task brief for seed placeholders in round 2 as well
            processed_brief = self._process_seed_placeholders(task_brief, email)
            
            # Build checks text for round 2 validation
            checks_text = ""
            if checks:
                processed_checks = [self._process_seed_placeholders(check, email) for check in checks]
                checks_list = "\n".join([f"- {check}" for check in processed_checks])
                checks_text = f"""

VALIDATION REQUIREMENTS - Your revised implementation MUST satisfy ALL of these checks:
{checks_list}

CRITICAL: Pay special attention to these validation requirements. If any were failing in the previous version, ensure they pass in your revision."""

            # Build attachments text for round 2
            attachments_text = ""
            if attachments:
                attachments_info = []
                for attachment in attachments:
                    name = attachment.get('name', 'unknown')
                    url = attachment.get('url', '')
                    if url.startswith('data:'):
                        if 'base64,' in url:
                            content_type = url.split(';')[0].replace('data:', '')
                            attachments_info.append(f"- {name} ({content_type}): Base64 encoded content provided")
                        else:
                            attachments_info.append(f"- {name}: Data URL provided")
                    else:
                        attachments_info.append(f"- {name}: {url}")
                
                attachments_text = f"""

ATTACHMENTS PROVIDED:
{chr(10).join(attachments_info)}

IMPORTANT: Ensure attachments are properly processed and integrated into the revised application."""

            user_prompt = f"""REVISION REQUEST - ROUND 2 IMPROVEMENTS:

ORIGINAL TASK BRIEF:
{processed_brief}

CURRENT IMPLEMENTATION TO REVISE:
{json.dumps(existing_files or {}, indent=2)}

IMPROVEMENT INSTRUCTIONS:
This is Round 2 - you need to significantly improve the existing application. Common areas for enhancement include:

1. **Bug Fixes**: Fix any functional issues, JavaScript errors, or broken features
2. **User Experience**: Improve the interface, add better visual feedback, enhance usability
3. **Functionality**: Add more features, better error handling, input validation
4. **Design**: Enhance the visual appearance, improve responsive design, add animations
5. **Performance**: Optimize code, reduce redundancy, improve efficiency
6. **Accessibility**: Add ARIA labels, keyboard navigation, better semantic HTML
7. **Robustness**: Handle edge cases, add proper form validation, improve error messages

{checks_text}{attachments_text}

SPECIFIC REVISION REQUIREMENTS:
- Maintain all existing functionality that works correctly
- Significantly improve the user interface and user experience
- Add proper error handling and user feedback
- Ensure all validation checks pass
- Make the application more polished and professional
- Add helpful features that enhance the core functionality
- Improve code organization and comments

IMPORTANT: Your response must be valid JSON only. Use this exact format:
{{"index_html": "<!DOCTYPE html>...", "style_css": "body {{...", "script_js": "// code here", "readme_md": "# title"}}

Make sure to properly escape all quotes and newlines in the JSON strings. Do not use backticks or template literals."""
            
            result = await self._code_reviser.run(user_prompt) #type: ignore
        
        # Get the AI output - it's in JSON format
        import json
        import re
        try:
            # The output is a JSON string containing the files
            if hasattr(result, 'output'):
                output_text = result.output
                self.logger.info(f"Raw AI output: {output_text[:200]}...")
                
                # Extract JSON from the output (it might be wrapped in ```json blocks)
                if '```json' in output_text:
                    start = output_text.find('```json') + 7
                    end = output_text.find('```', start)
                    json_text = output_text[start:end].strip()
                else:
                    json_text = output_text.strip()
                
                # Fix template literals (backticks) to proper JSON strings
                # This handles multiline strings that use backticks properly
                def replace_template_literal(match):
                    content = match.group(1)
                    # Properly escape the content for JSON
                    return json.dumps(content)
                
                # Replace template literals with proper JSON strings
                json_text = re.sub(r'`((?:[^`\\]|\\.)*)(?<!\\)`', replace_template_literal, json_text, flags=re.DOTALL)
                
                # Additional JSON fixes for common AI errors
                # Fix unescaped newlines in string values (common with base64)
                # This regex finds string values that contain literal newlines and fixes them
                def fix_multiline_strings(text):
                    # Find patterns like: "key": "value with
                    # newline"
                    # And convert to: "key": "value with\\nnewline"
                    lines = text.split('\n')
                    result_lines = []
                    in_string = False
                    string_start_char = None
                    
                    for i, line in enumerate(lines):
                        # Track if we're inside a JSON string value
                        # This is a simplified approach - count quotes
                        fixed_line = line
                        
                        # Check if previous line ended with an incomplete string
                        if in_string and i > 0:
                            # This line is continuation of a string - escape it
                            fixed_line = line.replace('"', '\\"')
                            # Add back to previous line with escaped newline
                            result_lines[-1] = result_lines[-1].rstrip() + '\\n' + fixed_line
                            
                            # Check if string ends on this line
                            if '"' in line and not line.rstrip().endswith('\\'):
                                in_string = False
                            continue
                        
                        # Check if this line starts a multiline string
                        # Pattern: "key": "value... (no closing quote)
                        if '": "' in line or "': '" in line:
                            quote_char = '"' if '": "' in line else "'"
                            parts = line.split(f'{quote_char}: {quote_char}')
                            if len(parts) > 1:
                                value_part = parts[-1]
                                # Count quotes to see if string is closed
                                quote_count = value_part.count(quote_char)
                                # If odd number, string continues to next line
                                if quote_count % 2 == 0 and not value_part.rstrip().endswith(quote_char):
                                    in_string = True
                                    string_start_char = quote_char
                        
                        result_lines.append(fixed_line)
                    
                    return '\n'.join(result_lines)
                
                # Try to parse directly first
                try:
                    result_data = json.loads(json_text)
                except json.JSONDecodeError as first_error:
                    self.logger.warning(f"Initial JSON parse failed: {first_error}, attempting fixes...")
                    
                    # Try fixing multiline strings
                    try:
                        fixed_json = fix_multiline_strings(json_text)
                        result_data = json.loads(fixed_json)
                        self.logger.info("Successfully parsed JSON after multiline fix")
                    except json.JSONDecodeError as second_error:
                        # Last resort: try to extract individual fields manually
                        self.logger.warning(f"Multiline fix failed: {second_error}, attempting manual extraction...")
                        result_data = self._extract_json_fields_manually(json_text)
                        if not result_data:
                            raise first_error  # Re-raise original error
                
                return {
                    "index.html": result_data.get('index_html', ''),
                    "style.css": result_data.get('style_css', ''),
                    "script.js": result_data.get('script_js', ''),
                    "README.md": result_data.get('readme_md', '')
                }
            else:
                raise Exception("No output found in AI result")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI JSON output: {e}")
            self.logger.error(f"Raw output: {result.output}")
            raise Exception(f"AI returned invalid JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error processing AI result: {e}")
            raise Exception(f"Failed to process AI result: {e}")