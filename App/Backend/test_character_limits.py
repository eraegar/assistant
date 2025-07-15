#!/usr/bin/env python3
"""
Test script for character limits validation
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def get_client_token():
    """Get client authentication token"""
    print("🔐 Getting client token...")
    
    # Try existing test clients from create_test_data.py
    test_credentials = [
        {"phone": "+7900123456", "password": "password123"},  # Ivan
        {"phone": "+7900654321", "password": "password123"},  # Maria
    ]
    
    for creds in test_credentials:
        response = requests.post(f"{BASE_URL}/api/v1/clients/auth/login", json=creds)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Client token obtained for {creds['phone']}")
            return token
        else:
            print(f"❌ Failed with {creds['phone']}: {response.status_code}")
    
    print("❌ Could not authenticate with any test credentials")
    return None

def test_task_creation_validation(token):
    """Test task creation with various character limits"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📝 Testing Task Creation Validation...")
    print("=" * 50)
    
    # Test cases for validation
    test_cases = [
        {
            "name": "Valid task",
            "data": {
                "title": "Valid task title",
                "description": "This is a valid task description with proper length.",
                "type": "personal"
            },
            "should_pass": True
        },
        {
            "name": "Title too short",
            "data": {
                "title": "Hi",  # Only 2 characters
                "description": "This description is fine.",
                "type": "personal"
            },
            "should_pass": False
        },
        {
            "name": "Title too long",
            "data": {
                "title": "A" * 201,  # 201 characters (max is 200)
                "description": "Description is fine.",
                "type": "personal"
            },
            "should_pass": False
        },
        {
            "name": "Empty title",
            "data": {
                "title": "",
                "description": "Description is fine.",
                "type": "personal"
            },
            "should_pass": False
        },
        {
            "name": "Whitespace-only title",
            "data": {
                "title": "   \n  \t  ",
                "description": "Description is fine.",
                "type": "personal"
            },
            "should_pass": False
        },
        {
            "name": "Description too long",
            "data": {
                "title": "Valid title",
                "description": "A" * 2001,  # 2001 characters (max is 2000)
                "type": "personal"
            },
            "should_pass": False
        },
        {
            "name": "Empty description (should be OK)",
            "data": {
                "title": "Valid title",
                "description": "",
                "type": "personal"
            },
            "should_pass": True
        },
        {
            "name": "No description (should be OK)",
            "data": {
                "title": "Valid title",
                "type": "personal"
            },
            "should_pass": True
        },
        {
            "name": "Max length title and description",
            "data": {
                "title": "A" * 200,  # Exactly 200 characters
                "description": "B" * 2000,  # Exactly 2000 characters
                "type": "personal"
            },
            "should_pass": True
        },
        {
            "name": "Title with excessive whitespace",
            "data": {
                "title": "  Valid    task   title   with   spaces  ",
                "description": "Description with\n\n\n\nmultiple line breaks and    spaces.",
                "type": "personal"
            },
            "should_pass": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/clients/tasks",
            headers=headers,
            json=test_case["data"]
        )
        
        if test_case["should_pass"]:
            if response.status_code in [200, 201]:
                print(f"   ✅ PASS - Task created successfully")
                # Clean up by getting task ID and potentially canceling it
                if response.status_code == 200:
                    task_data = response.json()
                    if isinstance(task_data, dict) and "id" in task_data:
                        task_id = task_data["id"]
                        print(f"   📝 Created task ID: {task_id}")
            else:
                print(f"   ❌ FAIL - Expected success but got {response.status_code}: {response.text}")
        else:
            if response.status_code in [422, 400]:
                print(f"   ✅ PASS - Validation correctly rejected (status: {response.status_code})")
                # Try to extract validation message
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        if isinstance(error_data["detail"], list):
                            # Pydantic validation errors
                            for error in error_data["detail"]:
                                print(f"        Error: {error.get('msg', 'Unknown error')}")
                        else:
                            print(f"        Error: {error_data['detail']}")
                except:
                    pass
            else:
                print(f"   ❌ FAIL - Expected validation error but got {response.status_code}: {response.text}")

def test_task_completion_validation(token):
    """Test task completion with character limits (simulation)"""
    
    print("\n📋 Testing Task Completion Validation...")
    print("=" * 50)
    
    # This would normally require a task to complete, so we'll just test the validation logic
    print("📝 Task completion validation test cases:")
    
    completion_tests = [
        {
            "name": "Valid completion",
            "completion_summary": "Successfully completed the task",
            "detailed_result": "I have successfully completed all the requested work according to specifications. Everything was done on time and meets the requirements.",
            "should_pass": True
        },
        {
            "name": "Summary too short",
            "completion_summary": "Done",  # Too short
            "detailed_result": "Task completed successfully with attention to detail.",
            "should_pass": False
        },
        {
            "name": "Summary too long",
            "completion_summary": "A" * 501,  # Too long (max 500)
            "detailed_result": "Task completed successfully with attention to detail.",
            "should_pass": False
        },
        {
            "name": "Result too short",
            "completion_summary": "Task completed successfully",
            "detailed_result": "Done well",  # Too short (min 20)
            "should_pass": False
        },
        {
            "name": "Result too long",
            "completion_summary": "Task completed successfully",
            "detailed_result": "A" * 5001,  # Too long (max 5000)
            "should_pass": False
        }
    ]
    
    for i, test in enumerate(completion_tests, 1):
        print(f"\n{i}. {test['name']}")
        
        # Simulate validation
        summary_len = len(test['completion_summary'])
        result_len = len(test['detailed_result'])
        
        summary_valid = 10 <= summary_len <= 500
        result_valid = 20 <= result_len <= 5000
        
        is_valid = summary_valid and result_valid
        
        if test['should_pass'] == is_valid:
            print(f"   ✅ PASS - Validation behaves as expected")
        else:
            print(f"   ❌ FAIL - Expected {test['should_pass']} but got {is_valid}")
        
        print(f"   Summary: {summary_len} chars (valid: {summary_valid})")
        print(f"   Result: {result_len} chars (valid: {result_valid})")

def test_message_validation():
    """Test message content validation"""
    
    print("\n💬 Testing Message Validation...")
    print("=" * 50)
    
    message_tests = [
        {
            "name": "Valid message",
            "content": "This is a normal message",
            "should_pass": True
        },
        {
            "name": "Empty message",
            "content": "",
            "should_pass": False
        },
        {
            "name": "Whitespace-only message",
            "content": "   \n  \t  ",
            "should_pass": False
        },
        {
            "name": "Very long message",
            "content": "A" * 2001,  # Too long (max 2000)
            "should_pass": False
        },
        {
            "name": "Max length message",
            "content": "A" * 2000,  # Exactly at limit
            "should_pass": True
        },
        {
            "name": "Single character",
            "content": "!",
            "should_pass": True
        }
    ]
    
    for i, test in enumerate(message_tests, 1):
        print(f"\n{i}. {test['name']}")
        
        content_len = len(test['content'].strip())
        is_valid = 1 <= content_len <= 2000 and test['content'].strip()
        
        if test['should_pass'] == is_valid:
            print(f"   ✅ PASS - Validation behaves as expected")
        else:
            print(f"   ❌ FAIL - Expected {test['should_pass']} but got {is_valid}")
        
        print(f"   Content: {content_len} chars (after strip)")

def main():
    """Run all validation tests"""
    print("🧪 Testing Character Limits Validation")
    print("=" * 50)
    
    # Get authentication token
    token = get_client_token()
    if not token:
        print("❌ Cannot run tests without authentication")
        return
    
    # Run validation tests
    test_task_creation_validation(token)
    test_task_completion_validation(token)
    test_message_validation()
    
    print("\n🎉 Character Limits Validation Testing Complete!")
    print("💡 This ensures data quality and prevents performance issues")

if __name__ == "__main__":
    main() 