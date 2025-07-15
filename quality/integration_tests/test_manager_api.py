#!/usr/bin/env python3
"""
Test script for Manager API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_manager_registration():
    """Test manager registration"""
    print("🔧 Testing manager registration...")
    
    data = {
        "name": "Анна Менеджер",
        "phone": "+7900777777",
        "email": "anna.manager@example.com",
        "password": "manager123",
        "department": "Operations",
        "telegram_username": "@anna_manager"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/auth/register",
        headers=HEADERS,
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Manager registration successful")
        return True
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️ Manager already registered, skipping")
        return True
    else:
        print("❌ Manager registration failed")
        return False

def test_manager_login():
    """Test manager login"""
    print("\n🔐 Testing manager login...")
    
    data = {
        "phone": "+7900777777",
        "password": "manager123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/auth/login",
        headers=HEADERS,
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Response: {response_data}")
        
        if response.status_code == 200:
            print("✅ Manager login successful")
            token = response_data["access_token"]
            return token
        else:
            print("❌ Manager login failed")
            return None
    except:
        print(f"Raw response: {response.text}")
        print("❌ Manager login failed")
        return None

def test_manager_profile(token):
    """Test getting manager profile"""
    print("\n👤 Testing manager profile...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/profile",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Manager profile retrieval successful")
            return True
        else:
            print("❌ Manager profile retrieval failed")
            return False
    except:
        print(f"Raw response: {response.text}")
        print("❌ Manager profile retrieval failed")
        return False

def test_overview_analytics(token):
    """Test getting overview analytics"""
    print("\n📊 Testing overview analytics...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/dashboard/overview",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            print("✅ Overview analytics retrieval successful")
            return True
        else:
            print(f"Error response: {response.text}")
            print("❌ Overview analytics retrieval failed")
            return False
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        print("❌ Overview analytics retrieval failed")
        return False

def test_all_tasks(token):
    """Test getting all tasks"""
    print("\n📋 Testing all tasks retrieval...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/tasks?limit=5",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    response_data = response.json()
    print(f"Found {len(response_data.get('tasks', []))} tasks")
    
    if response.status_code == 200:
        print("✅ All tasks retrieval successful")
        return response_data.get('tasks', [])
    else:
        print("❌ All tasks retrieval failed")
        return []

def test_all_assistants(token):
    """Test getting all assistants"""
    print("\n👥 Testing all assistants retrieval...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/assistants?limit=5",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    response_data = response.json()
    print(f"Found {len(response_data.get('assistants', []))} assistants")
    
    # Print assistant details
    for assistant in response_data.get('assistants', []):
        print(f"  - {assistant['name']} ({assistant['specialization']}) - {assistant['status']}")
    
    if response.status_code == 200:
        print("✅ All assistants retrieval successful")
        return response_data.get('assistants', [])
    else:
        print("❌ All assistants retrieval failed")
        return []

def test_all_clients(token):
    """Test getting all clients"""
    print("\n👤 Testing all clients retrieval...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?limit=5",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print(f"Found {len(response_data.get('clients', []))} clients")
            
            # Print client details
            for client in response_data.get('clients', []):
                subscription = client.get('subscription')
                subscription_info = f" (подписка: {subscription['plan']})" if subscription else " (без подписки)"
                print(f"  - {client['name']}{subscription_info} - {client['total_tasks']} задач")
            
            print("✅ All clients retrieval successful")
            return response_data.get('clients', [])
        else:
            print(f"Error response: {response.text}")
            print("❌ All clients retrieval failed")
            return []
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")
        print("❌ All clients retrieval failed")
        return []

def test_task_filtering(token):
    """Test task filtering"""
    print("\n🔍 Testing task filtering...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    # Test filtering by status
    statuses = ['pending', 'in_progress', 'completed']
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/api/v1/management/tasks?status={status}&limit=3",
            headers=headers
        )
        
        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"  Status '{status}': {len(tasks)} tasks")
        else:
            print(f"  Status '{status}': Error {response.status_code}")
    
    print("✅ Task filtering test completed")

def test_assistant_filtering(token):
    """Test assistant filtering"""
    print("\n🔍 Testing assistant filtering...")
    
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {token}"
    }
    
    # Test filtering by status
    statuses = ['online', 'offline']
    
    for status in statuses:
        response = requests.get(
            f"{BASE_URL}/api/v1/management/assistants?status={status}&limit=3",
            headers=headers
        )
        
        if response.status_code == 200:
            assistants = response.json().get('assistants', [])
            print(f"  Status '{status}': {len(assistants)} assistants")
        else:
            print(f"  Status '{status}': Error {response.status_code}")
    
    print("✅ Assistant filtering test completed")

def main():
    """Run all tests"""
    print("🚀 Starting Manager API tests...\n")
    
    # Test registration
    if not test_manager_registration():
        print("Registration failed, stopping tests")
        return
    
    # Test login
    token = test_manager_login()
    if not token:
        print("Login failed, stopping tests")
        return
    
    # Test profile
    test_manager_profile(token)
    
    # Test overview analytics
    test_overview_analytics(token)
    
    # Test data retrieval
    tasks = test_all_tasks(token)
    assistants = test_all_assistants(token)
    clients = test_all_clients(token)
    
    # Test filtering if we have data
    if tasks:
        test_task_filtering(token)
    
    if assistants:
        test_assistant_filtering(token)
    
    print("\n✅ All Manager API tests completed!")
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"  - Found {len(tasks)} tasks")
    print(f"  - Found {len(assistants)} assistants") 
    print(f"  - Found {len(clients)} clients")

if __name__ == "__main__":
    main() 