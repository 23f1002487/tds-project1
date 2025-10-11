#!/usr/bin/env python3
"""
Test script to verify the student API workflow
This script tests both round 1 and round 2 task processing
"""

import requests
import json
import time
import sys
import os

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_SECRET = "1004@vsA"  # Use the secret from the template
TEST_EMAIL = "test@example.com"

def test_health_check():
    """Test if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the API is running on port 8000")
        return False

def test_round_1_task():
    """Test round 1 task submission"""
    print("\n🧪 Testing Round 1 Task Submission...")
    
    payload = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": "captcha-solver-test-1",
        "round": 1,
        "nonce": "test-nonce-123",
        "brief": "Create a captcha solver that handles ?url=https://example.com/captcha.png. Default to attached sample.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays captcha URL passed at ?url=...",
            "Page displays solved captcha text within 15 seconds"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": [
            {
                "name": "sample.png",
                "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Round 1 task submitted successfully")
                print(f"   Response: {result.get('message')}")
                return True
            else:
                print(f"❌ Unexpected response: {result}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting round 1 task: {str(e)}")
        return False

def test_round_2_task():
    """Test round 2 task submission"""
    print("\n🧪 Testing Round 2 Task Submission...")
    
    payload = {
        "email": TEST_EMAIL,
        "secret": TEST_SECRET,
        "task": "captcha-solver-test-1",  # Same task as round 1
        "round": 2,
        "nonce": "test-nonce-123",  # Same nonce as round 1
        "brief": "Update the captcha solver to handle SVG images and improve the UI design.",
        "checks": [
            "Handles SVG images",
            "Improved UI design",
            "README.md updated",
            "All previous functionality maintained"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": []
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Round 2 task submitted successfully")
                print(f"   Response: {result.get('message')}")
                return True
            else:
                print(f"❌ Unexpected response: {result}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting round 2 task: {str(e)}")
        return False

def test_invalid_secret():
    """Test with invalid secret"""
    print("\n🧪 Testing Invalid Secret...")
    
    payload = {
        "email": TEST_EMAIL,
        "secret": "wrong-secret",
        "task": "test-task",
        "round": 1,
        "nonce": "test-nonce",
        "brief": "Test brief",
        "checks": ["Test check"],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload)
        
        if response.status_code == 403:
            print("✅ Invalid secret correctly rejected")
            return True
        else:
            print(f"❌ Expected 403, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing invalid secret: {str(e)}")
        return False

def test_invalid_payload():
    """Test with invalid payload structure"""
    print("\n🧪 Testing Invalid Payload...")
    
    payload = {
        "email": "invalid-email",  # Invalid email format
        "secret": TEST_SECRET,
        "task": "",  # Empty task
        "round": 0,  # Invalid round
        "brief": "Test brief",
        "checks": [],  # Empty checks
        "evaluation_url": "not-a-url",  # Invalid URL
        "attachments": []
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload)
        
        if response.status_code == 422:  # Validation error
            print("✅ Invalid payload correctly rejected")
            return True
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing invalid payload: {str(e)}")
        return False

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting API Workflow Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Invalid Secret", test_invalid_secret),
        ("Invalid Payload", test_invalid_payload),
        ("Round 1 Task", test_round_1_task),
        ("Round 2 Task", test_round_2_task),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "health":
            test_health_check()
        elif sys.argv[1] == "round1":
            test_round_1_task()
        elif sys.argv[1] == "round2":
            test_round_2_task()
        else:
            print("Usage: python test_workflow.py [health|round1|round2]")
    else:
        run_all_tests()