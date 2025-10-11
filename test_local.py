#!/usr/bin/env python3
"""
Test script for the TDS P1 Web App Generator API
"""
import requests
import json
import time

API_BASE = "http://localhost:7860"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root test failed: {e}")
        return False

def test_simple_task():
    """Test a simple task processing"""
    print("\n🚀 Testing Simple Task Processing...")
    
    payload = {
        "email": "23f1002487@ds.study.iitm.ac.in",
        "secret": "this-is-agni",
        "task": "hello-world",
        "round": 1,
        "nonce": "test-001",
        "brief": "Create a simple HTML page that displays 'Hello World' in large text",
        "checks": ["Page displays Hello World text"],
        "evaluation_url": "https://httpbin.org/post"
    }
    
    try:
        response = requests.post(f"{API_BASE}/process_task", json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Task processing successful!")
            print(f"Repository: {result.get('repo_url', 'N/A')}")
            print(f"Pages URL: {result.get('pages_url', 'N/A')}")
            return True
        else:
            print(f"❌ Task processing failed: {response.text}")
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (this might be normal for AI processing)")
        return False
    except Exception as e:
        print(f"❌ Task processing error: {e}")
        return False

def test_calculator_task():
    """Test the calculator task from test_request.json"""
    print("\n🧮 Testing Calculator Task...")
    
    try:
        with open('test_request.json', 'r') as f:
            payload = json.load(f)
    except FileNotFoundError:
        print("❌ test_request.json not found")
        return False
    
    try:
        response = requests.post(f"{API_BASE}/process_task", json=payload, timeout=120)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Calculator task successful!")
            print(f"Repository: {result.get('repo_url', 'N/A')}")
            print(f"Pages URL: {result.get('pages_url', 'N/A')}")
            return True
        else:
            print(f"❌ Calculator task failed: {response.text}")
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (AI processing can take time)")
        return False
    except Exception as e:
        print(f"❌ Calculator task error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TDS P1 Web App Generator - Local Testing")
    print("=" * 50)
    
    # Basic endpoint tests
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok:
        print("\n❌ Health check failed - stopping tests")
        exit(1)
    
    print(f"\n📊 Basic Tests: Health {'✅' if health_ok else '❌'} | Root {'✅' if root_ok else '❌'}")
    
    # Task processing tests
    print("\n" + "=" * 50)
    print("🔄 Starting Task Processing Tests...")
    print("⚠️  Note: These tests require valid environment variables:")
    print("   - OPENAI_API_KEY (your AIPIPE token)")
    print("   - OPENAI_BASE_URL (AIPIPE URL)")
    print("   - github_token")
    print("   - secret")
    
    input("\nPress Enter to continue with task tests (or Ctrl+C to exit)...")
    
    simple_ok = test_simple_task()
    
    if simple_ok:
        calc_ok = test_calculator_task()
    else:
        print("⚠️  Skipping calculator test due to simple test failure")
        calc_ok = False
    
    print("\n" + "=" * 50)
    print("📊 Final Results:")
    print(f"✅ Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ Root: {'PASS' if root_ok else 'FAIL'}")
    print(f"✅ Simple Task: {'PASS' if simple_ok else 'FAIL'}")
    print(f"✅ Calculator Task: {'PASS' if calc_ok else 'FAIL'}")
    
    if all([health_ok, root_ok, simple_ok]):
        print("\n🎉 Core functionality working!")
    else:
        print("\n⚠️  Some tests failed - check logs and environment variables")