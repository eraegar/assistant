#!/usr/bin/env python3
"""
Comprehensive test script for the Task Assignment System
Tests: task creation, auto-assignment, marketplace, timeout handling
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

class TaskSystemTester:
    def __init__(self):
        self.client_token = None
        self.assistant_token = None
        self.manager_token = None
        self.created_tasks = []
    
    def test_client_registration_and_login(self):
        """Test client registration and login"""
        print("\n🔐 Testing Client Authentication...")
        
        # Register client
        client_data = {
            "name": "Test Client",
            "phone": "+79001234567",
            "password": "testpass123",
            "telegram_username": "@testclient"
        }
        
        response = requests.post(f"{BASE_URL}/clients/auth/register", json=client_data)
        print(f"Client registration: {response.status_code}")
        
        if response.status_code == 400:
            print("Client already exists, trying login...")
        
        # Login client
        login_data = {
            "phone": "+79001234567",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/clients/auth/login", json=login_data)
        print(f"Client login: {response.status_code}")
        
        if response.status_code == 200:
            self.client_token = response.json()["access_token"]
            print("✅ Client authenticated successfully")
            return True
        else:
            print(f"❌ Client authentication failed: {response.text}")
            return False
    
    def test_assistant_registration_and_login(self):
        """Test assistant registration and login"""
        print("\n🔧 Testing Assistant Authentication...")
        
        # Register assistant
        assistant_data = {
            "name": "Test Assistant",
            "phone": "+79001234568",
            "password": "testpass123",
            "email": "assistant@test.com",
            "telegram_username": "@testassistant",
            "specialization": "full"
        }
        
        response = requests.post(f"{BASE_URL}/assistants/auth/register", json=assistant_data)
        print(f"Assistant registration: {response.status_code}")
        
        if response.status_code == 400:
            print("Assistant already exists, trying login...")
        
        # Login assistant
        login_data = {
            "phone": "+79001234568",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/assistants/auth/login", json=login_data)
        print(f"Assistant login: {response.status_code}")
        
        if response.status_code == 200:
            self.assistant_token = response.json()["access_token"]
            print("✅ Assistant authenticated successfully")
            
            # Set assistant status to online
            self.set_assistant_online()
            return True
        else:
            print(f"❌ Assistant authentication failed: {response.text}")
            return False
    
    def set_assistant_online(self):
        """Set assistant status to online"""
        print("\n🟢 Setting assistant status to online...")
        
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        status_data = {"status": "online"}
        
        response = requests.put(f"{BASE_URL}/assistants/profile/status", 
                              json=status_data, headers=headers)
        
        print(f"Assistant status update: {response.status_code}")
        if response.status_code == 200:
            print("✅ Assistant is now online")
        else:
            print(f"❌ Failed to set assistant online: {response.text}")
    
    def test_manager_authentication(self):
        """Test manager authentication"""
        print("\n📊 Testing Manager Authentication...")
        
        # Register manager first
        manager_data = {
            "name": "Test Manager",
            "phone": "+79001234569",
            "password": "manager123",
            "email": "manager@test.com",
            "department": "Operations"
        }
        
        response = requests.post(f"{BASE_URL}/management/auth/register", json=manager_data)
        print(f"Manager registration: {response.status_code}")
        
        if response.status_code == 400:
            print("Manager already exists, trying login...")
        
        # Login manager
        login_data = {
            "phone": "+79001234569",
            "password": "manager123"
        }
        
        response = requests.post(f"{BASE_URL}/management/auth/login", json=login_data)
        print(f"Manager login: {response.status_code}")
        
        if response.status_code == 200:
            self.manager_token = response.json()["access_token"]
            print("✅ Manager authenticated successfully")
            return True
        else:
            print(f"❌ Manager authentication failed: {response.text}")
            return False
    
    def test_task_creation_and_assignment(self):
        """Test task creation and automatic assignment"""
        print("\n📝 Testing Task Creation and Auto-Assignment...")
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # First, create a subscription for the client
        print("Creating subscription for client...")
        subscription_data = {
            "plan": "personal_2h",
            "payment_token": "test_payment_token_123"
        }
        
        subscription_response = requests.post(f"{BASE_URL}/clients/subscription/upgrade", 
                                            json=subscription_data, headers=headers)
        
        print(f"Subscription creation: {subscription_response.status_code}")
        if subscription_response.status_code != 200:
            print(f"Failed to create subscription: {subscription_response.text}")
        else:
            print("✅ Subscription created successfully")
        
        # Create a personal task
        task_data = {
            "title": "Test Personal Task",
            "description": "This is a test personal task for auto-assignment",
            "type": "personal"
        }
        
        response = requests.post(f"{BASE_URL}/clients/tasks", 
                               json=task_data, headers=headers)
        
        print(f"Task creation: {response.status_code}")
        
        if response.status_code == 200:
            task = response.json()
            self.created_tasks.append(task["id"])
            print(f"✅ Task created: ID={task['id']}, Status={task['status']}")
            
            # Check if task was auto-assigned
            if task.get("assistant_id"):
                print(f"🎯 Task auto-assigned to assistant {task['assistant_id']}")
            else:
                print("📍 Task sent to marketplace")
            
            return task
        else:
            print(f"❌ Task creation failed: {response.text}")
            return None
    
    def test_marketplace_functionality(self):
        """Test marketplace task browsing and claiming"""
        print("\n🛒 Testing Marketplace Functionality...")
        
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        
        # Get marketplace tasks
        response = requests.get(f"{BASE_URL}/assistants/tasks/marketplace", headers=headers)
        print(f"Marketplace tasks: {response.status_code}")
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Found {len(tasks)} tasks in marketplace")
            
            if tasks:
                # Try to claim the first task
                task_id = tasks[0]["id"]
                print(f"🎯 Attempting to claim task {task_id}")
                
                claim_response = requests.post(f"{BASE_URL}/assistants/tasks/{task_id}/claim", 
                                             headers=headers)
                
                print(f"Task claim: {claim_response.status_code}")
                if claim_response.status_code == 200:
                    print(f"✅ Successfully claimed task {task_id}")
                    return task_id
                else:
                    print(f"❌ Failed to claim task: {claim_response.text}")
            else:
                print("📭 No tasks in marketplace")
        else:
            print(f"❌ Failed to get marketplace tasks: {response.text}")
        
        return None
    
    def test_task_completion(self, task_id: int):
        """Test task completion flow"""
        print(f"\n✅ Testing Task Completion for task {task_id}...")
        
        headers = {"Authorization": f"Bearer {self.assistant_token}"}
        
        completion_data = {
            "completion_summary": "Test task completed successfully",
            "detailed_result": "This is a detailed result of the completed test task. All requirements were met."
        }
        
        response = requests.post(f"{BASE_URL}/assistants/tasks/{task_id}/complete", 
                               json=completion_data, headers=headers)
        
        print(f"Task completion: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Task {task_id} completed successfully")
            return True
        else:
            print(f"❌ Task completion failed: {response.text}")
            return False
    
    def test_client_task_approval(self, task_id: int):
        """Test client task approval"""
        print(f"\n👍 Testing Task Approval for task {task_id}...")
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        approval_data = {
            "rating": 5,
            "feedback": "Excellent work! Very satisfied with the results."
        }
        
        response = requests.post(f"{BASE_URL}/clients/tasks/{task_id}/approve", 
                               json=approval_data, headers=headers)
        
        print(f"Task approval: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Task {task_id} approved successfully")
            return True
        else:
            print(f"❌ Task approval failed: {response.text}")
            return False
    
    def test_marketplace_stats(self):
        """Test marketplace statistics for management"""
        print("\n📊 Testing Marketplace Statistics...")
        
        if not self.manager_token:
            print("❌ Manager not authenticated, skipping stats test")
            return
        
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        response = requests.get(f"{BASE_URL}/management/marketplace/stats", headers=headers)
        print(f"Marketplace stats: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Marketplace Statistics:")
            print(f"  - Total pending tasks: {stats.get('total_pending_tasks', 0)}")
            print(f"  - Overdue tasks: {stats.get('overdue_tasks', 0)}")
            print(f"  - Online assistants: {stats.get('online_assistants', 0)}")
            print(f"  - System health: {stats.get('system_health', 'unknown')}")
            
            if stats.get('recommendations'):
                print("  - Recommendations:")
                for rec in stats['recommendations']:
                    print(f"    • {rec}")
        else:
            print(f"❌ Failed to get marketplace stats: {response.text}")
    
    def run_full_test(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive Task System Test...")
        print("=" * 60)
        
        # Authentication tests
        if not self.test_client_registration_and_login():
            return False
        
        if not self.test_assistant_registration_and_login():
            return False
        
        self.test_manager_authentication()  # Optional
        
        # Task workflow tests
        task = self.test_task_creation_and_assignment()
        if not task:
            return False
        
        # Wait a moment for background processing
        print("\n⏳ Waiting for background processing...")
        time.sleep(5)
        
        # Marketplace tests
        claimed_task_id = self.test_marketplace_functionality()
        
        # Completion workflow (use claimed task or created task)
        test_task_id = claimed_task_id or task["id"]
        if self.test_task_completion(test_task_id):
            time.sleep(2)  # Wait for completion processing
            self.test_client_task_approval(test_task_id)
        
        # Management insights
        self.test_marketplace_stats()
        
        print("\n🎉 Test suite completed!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    tester = TaskSystemTester()
    
    try:
        success = tester.run_full_test()
        if success:
            print("✅ All tests completed successfully!")
        else:
            print("❌ Some tests failed!")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc() 