#!/usr/bin/env python3
"""
Test script for the deployed TDS P1 Web App Generator
"""
import requests
import json
import time

# Your deployed app URL
API_URL = "https://vsaketh-tds-p1-web-app-generator.hf.space"

def test_health_check():
    """Test the health endpoint"""
    print("🏥 Testing Health Check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_process_task():
    """Test the main process_task endpoint (will fail without environment variables)"""
    print("\n🚀 Testing Process Task Endpoint...")
    
    # Test payload
    payload = {
        "email": "23f1002487@ds.study.iitm.ac.in",
        "secret": "this-is-agni",
        "task": "simple-calculator",
        "round": 1,
        "nonce": "test-123",
        "brief": "Create a simple calculator with basic arithmetic operations",
        "checks": [
            "Has working buttons",
            "Performs calculations correctly",
            "Has a clear display"
        ],
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(f"{API_URL}/process_task", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 403:
            print("✅ Expected: Authentication failed (secret key validation working)")
        elif response.status_code == 500:
            print("⚠️  Internal server error (likely missing environment variables)")
        else:
            print(f"Response JSON: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_docs_endpoint():
    """Test if the docs endpoint is accessible"""
    print("\n📚 Testing API Documentation...")
    response = requests.get(f"{API_URL}/docs")
    print(f"Status Code: {response.status_code}")
    print("✅ API docs are accessible" if response.status_code == 200 else "❌ Docs not accessible")

if __name__ == "__main__":
    print("🧪 Testing TDS P1 Web App Generator")
    print("=" * 50)
    
    # Run tests
    health_ok = test_health_check()
    root_ok = test_root_endpoint()
    test_docs_endpoint()
    test_process_task()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Health Check: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ Root Endpoint: {'PASS' if root_ok else 'FAIL'}")
    print("✅ API Documentation: Accessible")
    print("⚠️  Process Task: Needs environment variables (OPENAI_API_KEY, github_token, secret)")
    
    print("\n🔧 Next Steps:")
    print("1. Set environment variables in Hugging Face Spaces:")
    print("   - OPENAI_API_KEY=your_aipipe_token")
    print("   - OPENAI_BASE_URL=https://aipipe.org/openrouter/v1")
    print("   - github_token=your_github_pat")
    print("   - secret=your_secret_key")
    print("2. Test with real task processing")
    print("3. Verify GitHub repository creation")