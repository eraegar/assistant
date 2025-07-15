#!/usr/bin/env python3
"""
Test script for Assistant API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_assistant_registration():
    """Test assistant registration"""
    print("🔧 Testing assistant registration...")
    
    data = {
        "name": "Анна Тестовая",
        "phone": "+7900555555",
        "email": "anna.test@example.com",
        "password": "testpass123",
        "specialization": "personal_only",
        "telegram_username": "@anna_test"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistants/auth/register",
        headers=HEADERS,
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Assistant registration successful")
        return True
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️ Assistant already registered, skipping")
        return True
    else:
        print("❌ Assistant registration failed")
        return False

def test_assistant_login():
    """Test assistant login"""
    print("\n🔐 Testing assistant login...")
    
    data = {
        "phone": "+7900555555",
        "password": "testpass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/assistants/auth/login",
        headers=HEADERS,
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Response: {response_data}")
        
        if response.status_code == 200:
            print("✅ Assistant login successful")
            token = response_data["access_token"]
            return token
        else:
            print("❌ Assistant login failed")
            return None
    except:
        print(f"Raw response: {response.text}")
        print("❌ Assistant login failed")
        return None

def test_assistant_profile(token):
    """Test getting assistant profile"""
    print("\n👤 Testing assistant profile...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/assistants/profile",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Assistant profile retrieval successful")
        return True
    else:
        print("❌ Assistant profile retrieval failed")
        return False

def test_status_update(token):
    """Test updating assistant status"""
    print("\n🔄 Testing status update...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    data = {"status": "online"}
    
    response = requests.put(
        f"{BASE_URL}/api/v1/assistants/profile/status",
        headers=headers,
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Status update successful")
        return True
    else:
        print("❌ Status update failed")
        return False

def test_marketplace_tasks(token):
    """Test getting marketplace tasks"""
    print("\n🛒 Testing marketplace tasks...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/assistants/tasks/marketplace",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Marketplace tasks retrieval successful")
        return True
    else:
        print("❌ Marketplace tasks retrieval failed")
        return False

def test_dashboard_stats(token):
    """Test getting dashboard stats"""
    print("\n📊 Testing dashboard stats...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/assistants/dashboard/stats",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Dashboard stats retrieval successful")
        return True
    else:
        print("❌ Dashboard stats retrieval failed")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Assistant API tests...\n")
    
    # Test registration
    if not test_assistant_registration():
        print("Registration failed, stopping tests")
        return
    
    # Test login
    token = test_assistant_login()
    if not token:
        print("Login failed, stopping tests")
        return
    
    # Test profile
    test_assistant_profile(token)
    
    # Test status update
    test_status_update(token)
    
    # Test marketplace tasks
    test_marketplace_tasks(token)
    
    # Test dashboard stats
    test_dashboard_stats(token)
    
    print("\n✅ All Assistant API tests completed!")

if __name__ == "__main__":
    main() 