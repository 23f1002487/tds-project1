#!/usr/bin/env python3
"""
Test script to verify environment variable configuration
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Config.config import config

def test_environment_variables():
    """Test that environment variables are loaded correctly"""
    
    print("🔧 Testing Environment Variable Configuration")
    print("=" * 50)
    
    # Test basic configuration
    print(f"Secret Key: {'✓ Set' if config.secret_key != '...' else '✗ Not Set'}")
    print(f"GitHub Token: {'✓ Set' if config.github_token != '...' else '✗ Not Set'}")
    print(f"AIPIPE Token: {'✓ Set' if config.aipipe_token else '✗ Not Set'}")
    print(f"AIPIPE URL: {config.aipipe_url}")
    print(f"OpenAI API Key: {'✓ Set' if config.openai_api_key else '✗ Not Set'}")
    print(f"OpenAI URL: {config.openai_url}")
    print(f"Log File: {config.log_file}")
    print(f"Log Level: {config.log_level}")
    
    # Test helper properties
    print(f"\nHelper Properties:")
    print(f"Has AI Key: {config.has_ai_key}")
    print(f"Get AI Key: {'✓ Set' if config.get_ai_key else '✗ Not Set'}")
    print(f"Get AI URL: {config.get_ai_url}")
    print(f"Has OpenAI Key: {config.has_openai_key}")
    
    # Test environment variable mapping
    print(f"\nEnvironment Variable Mapping:")
    env_vars = {
        'secret': config.secret_key,
        'github_token': config.github_token,
        'AIPIPE_TOKEN': config.aipipe_token,
        'AIPIPE_URL': config.aipipe_url,
        'OPENAI_API_KEY': config.openai_api_key,
        'OPENAI_URL': config.openai_url,
        'LOG_FILE': config.log_file,
        'LOG_LEVEL': config.log_level
    }
    
    for env_var, value in env_vars.items():
        env_value = os.getenv(env_var)
        if env_value:
            status = "✓ Matches" if str(value) == str(env_value) else "✗ Mismatch"
        else:
            status = "✗ Not Set" if value not in ['...', None] else "- Default"
        print(f"  {env_var}: {status}")

def test_ai_configuration():
    """Test AI service configuration logic"""
    
    print(f"\n🤖 Testing AI Configuration Logic")
    print("=" * 50)
    
    # Test which API key would be used
    api_key = config.get_ai_key
    ai_url = config.get_ai_url
    
    if config.aipipe_token:
        print(f"Primary API Key: AIPIPE Token (✓)")
        print(f"Service: AIPIPE")
        print(f"Model Format: openai/gpt-4.1-nano")
    elif config.openai_api_key:
        print(f"Primary API Key: OpenAI API Key (✓)")
        print(f"Service: Direct OpenAI")
        print(f"Model Format: openai:gpt-4.1-nano")
    else:
        print(f"Primary API Key: None (✗)")
        print(f"Service: None")
        print(f"Model Format: N/A")
    
    # Test URL configuration
    print(f"AI URL: {ai_url}")
    is_aipipe = "aipipe.org" in ai_url
    is_custom = ai_url not in ["https://api.openai.com/v1", "https://aipipe.org/openrouter/v1"]
    print(f"Using AIPIPE: {'✓ Yes' if is_aipipe else '✗ No'}")
    print(f"Custom URL: {'✓ Yes' if is_custom else '✗ No (using default)'}")
    
    # Test overall AI availability
    ai_available = config.has_ai_key
    print(f"AI Available: {'✓ Yes' if ai_available else '✗ No'}")

def print_setup_instructions():
    """Print setup instructions for missing configuration"""
    
    print(f"\n📋 Setup Instructions")
    print("=" * 50)
    
    if not config.has_ai_key:
        print("❌ AI Configuration Missing!")
        print("Set one of the following:")
        print(f"export AIPIPE_TOKEN=\"your_aipipe_token\"  # Recommended")
        print(f"export OPENAI_API_KEY=\"your_openai_api_key\"  # Alternative")
    else:
        print("✅ AI Configuration OK!")
    
    if config.github_token == "...":
        print("❌ GitHub Token Missing!")
        print(f"export github_token=\"your_github_personal_access_token\"")
    else:
        print("✅ GitHub Configuration OK!")

if __name__ == "__main__":
    test_environment_variables()
    test_ai_configuration()
    print_setup_instructions()

if __name__ == "__main__":
    test_environment_variables()
    test_ai_configuration()
    
    print(f"\n✅ Configuration test completed!")
    print(f"To set missing environment variables, use:")
    print(f"export secret=\"your_secret_key\"")
    print(f"export github_token=\"your_github_token\"")
    print(f"export AIPIPE_TOKEN=\"your_aipipe_token\"  # Recommended")
    print(f"export OPENAI_API_KEY=\"your_openai_api_key\"  # Alternative")
    print(f"export OPENAI_URL=\"your_custom_url\"")