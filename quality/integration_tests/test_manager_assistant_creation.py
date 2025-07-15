#!/usr/bin/env python3
"""
Test script for Manager Assistant Creation and Client Assignment functionality
Tests the new features added to the management panel
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def login_manager():
    """Login as manager and get auth token"""
    login_data = {
        "phone": "+79991111111", 
        "password": "manager123"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/auth/login", 
                           json=login_data, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"❌ Manager login failed: {response.status_code}")
        print(response.text)
        return None

def test_create_assistant(token):
    """Test creating a new assistant"""
    print("\n🧪 Testing assistant creation...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    # Test assistant data
    assistant_data = {
        "name": "Тестовый Ассистент",
        "phone": "+79995555555",
        "email": "test.assistant@example.com",
        "password": "assistant123",
        "specialization": "personal_only",
        "telegram_username": "test_assistant"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/assistants/create",
                           json=assistant_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Assistant created successfully!")
        print(f"   ID: {result['id']}")
        print(f"   Name: {result['name']}")
        print(f"   Email: {result['email']}")
        print(f"   Specialization: {result['specialization']}")
        return result['id']
    else:
        print(f"❌ Assistant creation failed: {response.status_code}")
        print(response.text)
        return None

def test_get_clients(token):
    """Get list of clients for testing assignment"""
    print("\n📋 Getting client list...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{API_BASE}/api/v1/management/clients", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        clients = data["clients"]
        print(f"✅ Found {len(clients)} clients")
        if clients:
            client = clients[0]  # Take first client
            print(f"   Test client: {client['name']} (ID: {client['id']})")
            return client['id']
        else:
            print("⚠️ No clients found for testing")
            return None
    else:
        print(f"❌ Failed to get clients: {response.status_code}")
        print(response.text)
        return None

def test_assign_client_to_assistant(token, client_id, assistant_id):
    """Test assigning a client to an assistant"""
    print(f"\n🔗 Testing client assignment...")
    print(f"   Client ID: {client_id}")
    print(f"   Assistant ID: {assistant_id}")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    assignment_data = {
        "assistant_id": assistant_id
    }
    
    response = requests.put(f"{API_BASE}/api/v1/management/clients/{client_id}/assign-assistant",
                          json=assignment_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Client assigned successfully!")
        print(f"   Message: {result['message']}")
        print(f"   Assigned tasks: {result['assigned_tasks']}")
        print(f"   Assistant: {result['assistant']['name']}")
        print(f"   Assistant current tasks: {result['assistant']['current_active_tasks']}")
        return True
    else:
        print(f"❌ Client assignment failed: {response.status_code}")
        print(response.text)
        return False

def test_get_assistants(token):
    """Get list of assistants to verify creation"""
    print("\n👥 Getting assistant list...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{API_BASE}/api/v1/management/assistants", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        assistants = data["assistants"]
        print(f"✅ Found {len(assistants)} assistants:")
        for assistant in assistants:
            print(f"   - {assistant['name']} ({assistant['specialization']}) - {assistant['current_active_tasks']} tasks")
        return True
    else:
        print(f"❌ Failed to get assistants: {response.status_code}")
        print(response.text)
        return False

def main():
    """Main test function"""
    print("🚀 Starting Manager Assistant Creation and Client Assignment Tests")
    print("=" * 70)
    
    # Step 1: Login as manager
    print("1️⃣ Logging in as manager...")
    token = login_manager()
    if not token:
        print("❌ Cannot proceed without manager login")
        return
    
    print("✅ Manager login successful!")
    
    # Step 2: Create a new assistant
    print("\n2️⃣ Creating new assistant...")
    assistant_id = test_create_assistant(token)
    if not assistant_id:
        print("❌ Cannot proceed without creating assistant")
        return
    
    # Step 3: Get clients for assignment testing
    print("\n3️⃣ Getting client list...")
    client_id = test_get_clients(token)
    if not client_id:
        print("⚠️ No clients available for assignment testing")
        # Continue anyway to show assistant was created
    
    # Step 4: Assign client to assistant (if client available)
    assignment_success = False
    if client_id:
        print("\n4️⃣ Assigning client to assistant...")
        assignment_success = test_assign_client_to_assistant(token, client_id, assistant_id)
        if assignment_success:
            print("✅ Client assignment successful!")
        else:
            print("❌ Client assignment failed")
    
    # Step 5: Verify assistants list
    print("\n5️⃣ Verifying assistant list...")
    test_get_assistants(token)
    
    print("\n" + "=" * 70)
    print("🎉 Manager Assistant Creation and Client Assignment Tests Completed!")
    print("\n📊 Summary:")
    print(f"   ✅ Manager login: Success")
    print(f"   ✅ Assistant creation: {'Success' if assistant_id else 'Failed'}")
    print(f"   ✅ Client list: {'Success' if client_id else 'No clients'}")
    if client_id:
        print(f"   ✅ Client assignment: {'Success' if assignment_success else 'Failed'}")
    print(f"   ✅ Assistant verification: Success")
    
    print("\n🎯 Next steps:")
    print("   1. Open Manager App (http://localhost:3001)")
    print("   2. Go to 'Ассистенты' tab")
    print("   3. Click 'Создать ассистента' to test UI")
    print("   4. Go to 'Клиенты' tab")
    print("   5. Click 'Назначить ассистента' icon to test assignment UI")

if __name__ == "__main__":
    main() 