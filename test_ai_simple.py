#!/usr/bin/env python3
"""
Simple test for AI Agent creation with new configuration
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_creation():
    """Test if Agent can be created with current configuration"""
    try:
        from pydantic_ai import Agent
        print("✅ pydantic_ai import successful")
        
        # Test with AIPIPE configuration
        os.environ["OPENAI_API_KEY"] = "test_token_12345"  # Dummy token for testing
        os.environ["OPENAI_BASE_URL"] = "https://aipipe.org/openrouter/v1"
        
        # Try to create an agent (should work even with dummy token for creation)
        agent = Agent(
            "gpt-4.1-nano",
            system_prompt="You are a test agent."
        )
        
        print("✅ Agent creation successful")
        print(f"Agent model: {agent.model}")
        return True
        
    except ImportError as e:
        print(f"❌ pydantic_ai import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_config():
    """Test the configuration loading"""
    try:
        from Config.config import config
        print("✅ Config import successful")
        print(f"Config openai_token: {'SET' if config.openai_token else 'NOT SET'}")
        print(f"Config aipipe_url: {config.aipipe_url}")
        print(f"Config github_token: {'SET' if config.github_token != '...' else 'NOT SET'}")
        print(f"Config secret: {'SET' if config.secret_key != '...' else 'NOT SET'}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_ai_service():
    """Test AI service initialization"""
    try:
        from services.ai_service import AIService
        print("✅ AIService import successful")
        
        ai_service = AIService()
        print(f"AI service initialized: {ai_service is not None}")
        print(f"Code generator available: {ai_service._code_generator is not None}")
        return True
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Configuration")
    print("=" * 40)
    
    config_ok = test_config()
    agent_ok = test_agent_creation()
    service_ok = test_ai_service()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Config: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Agent Creation: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    print(f"AI Service: {'✅ PASS' if service_ok else '❌ FAIL'}")
    
    if all([config_ok, agent_ok, service_ok]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed - check environment variables")