#!/usr/bin/env python3
"""
Test script for multiple assistants functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_manager_token():
    """Get manager authentication token"""
    login_data = {
        "phone": "+79089050077",
        "password": "admin32451124"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/management/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to login manager: {response.text}")
        return None

def test_primary_assignment(token):
    """Test assigning primary assistant"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing primary assistant assignment...")
    
    # Get clients
    response = requests.get(f"{BASE_URL}/api/v1/management/clients", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get clients: {response.text}")
        return False
        
    clients = response.json()["clients"]
    if not clients:
        print("No clients found")
        return False
        
    client = clients[0]
    print(f"Using client: {client['name']} (ID: {client['id']})")
    
    # Get assistants
    response = requests.get(f"{BASE_URL}/api/v1/management/assistants", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get assistants: {response.text}")
        return False
        
    assistants = response.json()["assistants"]
    if len(assistants) < 2:
        print("Need at least 2 assistants for testing")
        return False
        
    # Try to assign primary assistant
    assistant1 = assistants[0]
    assignment_data = {"assistant_id": assistant1["id"]}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/clients/{client['id']}/assign-primary-assistant",
        headers=headers,
        json=assignment_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Primary assistant assigned successfully: {result['message']}")
        return True
    else:
        print(f"❌ Failed to assign primary assistant: {response.text}")
        return False

def test_additional_assignment(token):
    """Test assigning additional assistant"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing additional assistant assignment...")
    
    # Get clients
    response = requests.get(f"{BASE_URL}/api/v1/management/clients", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get clients: {response.text}")
        return False
        
    clients = response.json()["clients"]
    if not clients:
        print("No clients found")
        return False
        
    client = clients[0]
    
    # Get assistants
    response = requests.get(f"{BASE_URL}/api/v1/management/assistants", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get assistants: {response.text}")
        return False
        
    assistants = response.json()["assistants"]
    if len(assistants) < 2:
        print("Need at least 2 assistants for testing")
        return False
        
    # Try to assign additional assistant
    assistant2 = assistants[1]
    assignment_data = {"assistant_id": assistant2["id"]}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/clients/{client['id']}/assign-additional-assistant",
        headers=headers,
        json=assignment_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Additional assistant assigned successfully: {result['message']}")
        return True
    else:
        print(f"❌ Failed to assign additional assistant: {response.text}")
        return False

def test_assignment_listing(token):
    """Test listing assignments with primary status"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing assignment listing...")
    
    response = requests.get(f"{BASE_URL}/api/v1/management/assignments", headers=headers)
    if response.status_code != 200:
        print(f"Failed to get assignments: {response.text}")
        return False
        
    assignments = response.json()["assignments"]
    print(f"Found {len(assignments)} assignments:")
    
    for assignment in assignments:
        primary_status = "PRIMARY" if assignment["is_primary"] else "ADDITIONAL"
        print(f"  - {assignment['client']['name']} ↔ {assignment['assistant']['name']} ({primary_status})")
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Multiple Assistants Functionality")
    print("=" * 50)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Manager authenticated successfully")
    
    # Test assignment listing
    if not test_assignment_listing(token):
        return
    
    # Test primary assignment (might fail if already assigned)
    test_primary_assignment(token)
    
    # Test additional assignment
    test_additional_assignment(token)
    
    # Test final listing
    print("\n🔍 Final assignment status:")
    test_assignment_listing(token)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    main() 