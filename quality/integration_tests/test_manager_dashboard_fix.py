#!/usr/bin/env python3
"""
Тест для проверки исправлений в менеджер-панели:
1. Создание ассистента
2. Загрузка доступных ассистентов для переназначения задач
3. Назначение клиента ассистенту
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
        print(f"✅ Manager login successful. Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Manager login failed: {response.status_code} - {response.text}")
        return None

def test_available_assistants_endpoint(token):
    """Test the available assistants endpoint"""
    print("\n🔍 Testing available assistants endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test without task type filter
    response = requests.get(f"{API_BASE}/api/v1/management/assistants/available", headers=headers)
    
    if response.status_code == 200:
        assistants = response.json()
        print(f"✅ Available assistants loaded successfully. Count: {len(assistants)}")
        for assistant in assistants:
            print(f"   - {assistant['name']} ({assistant['specialization']}) - {assistant['current_active_tasks']}/5 tasks")
        
        # Test with personal task type filter
        response_personal = requests.get(f"{API_BASE}/api/v1/management/assistants/available?task_type=personal", headers=headers)
        if response_personal.status_code == 200:
            personal_assistants = response_personal.json()
            print(f"✅ Personal assistants filtered successfully. Count: {len(personal_assistants)}")
        
        # Test with business task type filter
        response_business = requests.get(f"{API_BASE}/api/v1/management/assistants/available?task_type=business", headers=headers)
        if response_business.status_code == 200:
            business_assistants = response_business.json()
            print(f"✅ Business assistants filtered successfully. Count: {len(business_assistants)}")
        
        return assistants
    else:
        print(f"❌ Available assistants endpoint failed: {response.status_code} - {response.text}")
        return []

def test_create_assistant(token):
    """Test creating a new assistant"""
    print("\n👥 Testing assistant creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    new_assistant_data = {
        "name": "Тестовый Ассистент Dashboard",
        "phone": "+79123456789",
        "email": "test.assistant.dashboard@example.com",
        "password": "testpass123",
        "specialization": "full_access",
        "telegram_username": "test_assistant_dash"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/assistants/create", 
                           headers=headers, 
                           json=new_assistant_data)
    
    if response.status_code == 200:
        assistant = response.json()
        print(f"✅ Assistant created successfully: ID {assistant['id']}, Name: {assistant['name']}")
        return assistant
    else:
        print(f"❌ Assistant creation failed: {response.status_code} - {response.text}")
        return None

def test_all_assistants_endpoint(token):
    """Test the all assistants endpoint to see if new assistant appears"""
    print("\n📋 Testing all assistants endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/api/v1/management/assistants", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        assistants = data.get('assistants', [])
        print(f"✅ All assistants loaded successfully. Total count: {len(assistants)}")
        
        # Show latest assistants
        print("   Latest assistants:")
        for assistant in assistants[-3:]:  # Show last 3
            print(f"   - ID: {assistant['id']}, Name: {assistant['name']}, Specialization: {assistant['specialization']}")
        
        return assistants
    else:
        print(f"❌ All assistants endpoint failed: {response.status_code} - {response.text}")
        return []

def test_dashboard_overview(token):
    """Test the dashboard overview endpoint"""
    print("\n📊 Testing dashboard overview...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/api/v1/management/dashboard/overview", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard overview loaded successfully")
        print(f"   Tasks: {data['tasks']['total']} total, {data['tasks']['pending']} pending")
        print(f"   Assistants: {data['assistants']['total_active']} total, {data['assistants']['online_now']} online")
        print(f"   Clients: {data['clients']['total_active']} total, {data['clients']['active_subscribers']} subscribers")
        print(f"   Revenue: {data['performance']['monthly_revenue']:,} ₽")
        return data
    else:
        print(f"❌ Dashboard overview failed: {response.status_code} - {response.text}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Manager Dashboard Fix Tests\n")
    
    # Test authentication
    token = test_manager_login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test dashboard overview
    test_dashboard_overview(token)
    
    # Test available assistants endpoint (should work now)
    available_assistants = test_available_assistants_endpoint(token)
    
    # Test creating a new assistant
    new_assistant = test_create_assistant(token)
    
    # Test loading all assistants to see if new one appears
    all_assistants = test_all_assistants_endpoint(token)
    
    # Test available assistants again to see if new assistant appears
    print("\n🔄 Re-testing available assistants after creation...")
    available_assistants_after = test_available_assistants_endpoint(token)
    
    print(f"\n📈 Summary:")
    print(f"   - Manager login: ✅")
    print(f"   - Available assistants endpoint: {'✅' if available_assistants else '❌'}")
    print(f"   - Assistant creation: {'✅' if new_assistant else '❌'}")
    print(f"   - All assistants endpoint: {'✅' if all_assistants else '❌'}")
    print(f"   - New assistant appears in available list: {'✅' if len(available_assistants_after) > len(available_assistants) else '❌'}")

if __name__ == "__main__":
    main() 