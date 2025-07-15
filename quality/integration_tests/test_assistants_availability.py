#!/usr/bin/env python3
"""
Тест для проверки доступности ассистентов в системе
"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
MANAGER_PHONE = "+79999999999"
MANAGER_PASSWORD = "manager123"

def test_manager_login():
    """Test manager authentication"""
    print("🔐 Testing manager login...")
    
    response = requests.post(f"{API_BASE}/api/v1/management/auth/login", json={
        "phone": MANAGER_PHONE,
        "password": MANAGER_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Manager login successful")
        return token
    else:
        print(f"❌ Manager login failed: {response.status_code} - {response.text}")
        return None

def check_assistants_data(token):
    """Check all assistants data"""
    print("\n📋 Checking all assistants data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/api/v1/management/assistants", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        assistants = data.get('assistants', [])
        print(f"✅ Found {len(assistants)} assistants")
        
        for assistant in assistants:
            print(f"\n📊 Assistant: {assistant['name']} (ID: {assistant['id']})")
            print(f"   Specialization: {assistant['specialization']}")
            print(f"   Status: {assistant['status']}")
            print(f"   Current active tasks: {assistant['current_active_tasks']}")
            print(f"   Total completed: {assistant['total_tasks_completed']}")
            print(f"   Average rating: {assistant['average_rating']}")
            print(f"   Is available: {assistant.get('is_available', 'NOT SET!')}")
            
        return assistants
    else:
        print(f"❌ Failed to get assistants: {response.status_code} - {response.text}")
        return []

def check_available_assistants(token):
    """Check available assistants endpoint"""
    print("\n🔍 Checking available assistants endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/api/v1/management/assistants/available", headers=headers)
    
    if response.status_code == 200:
        assistants = response.json()
        print(f"✅ Found {len(assistants)} available assistants")
        
        for assistant in assistants:
            print(f"\n🟢 Available Assistant: {assistant['name']} (ID: {assistant['id']})")
            print(f"   Specialization: {assistant['specialization']}")
            print(f"   Status: {assistant['status']}")
            print(f"   Current active tasks: {assistant['current_active_tasks']}")
            print(f"   Is available: {assistant.get('is_available', 'NOT SET!')}")
            
        return assistants
    else:
        print(f"❌ Failed to get available assistants: {response.status_code} - {response.text}")
        return []

def check_available_assistants_filtered(token, task_type):
    """Check available assistants with task type filter"""
    print(f"\n🎯 Checking available assistants for {task_type} tasks...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/api/v1/management/assistants/available?task_type={task_type}", headers=headers)
    
    if response.status_code == 200:
        assistants = response.json()
        print(f"✅ Found {len(assistants)} available assistants for {task_type} tasks")
        
        for assistant in assistants:
            print(f"   - {assistant['name']}: {assistant['specialization']} ({assistant['current_active_tasks']}/5 tasks)")
            
        return assistants
    else:
        print(f"❌ Failed to get available assistants for {task_type}: {response.status_code} - {response.text}")
        return []

def main():
    """Run all tests"""
    print("🚀 Starting Assistant Availability Tests\n")
    
    # Test authentication
    token = test_manager_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Check all assistants data
    all_assistants = check_assistants_data(token)
    
    # Check available assistants (no filter)
    available_assistants = check_available_assistants(token)
    
    # Check available assistants for personal tasks
    personal_assistants = check_available_assistants_filtered(token, "personal")
    
    # Check available assistants for business tasks
    business_assistants = check_available_assistants_filtered(token, "business")
    
    print(f"\n📈 Summary:")
    print(f"   - Total assistants: {len(all_assistants)}")
    print(f"   - Available assistants: {len(available_assistants)}")
    print(f"   - Available for personal tasks: {len(personal_assistants)}")
    print(f"   - Available for business tasks: {len(business_assistants)}")
    
    # Check if any assistants have is_available = True
    available_count = sum(1 for a in all_assistants if a.get('is_available', False))
    print(f"   - Assistants marked as available: {available_count}")
    
    if available_count == 0:
        print("\n⚠️  No assistants are marked as available!")
        print("This means all assistants have 5 or more active tasks.")

if __name__ == "__main__":
    main() 