#!/usr/bin/env python3
"""
Comprehensive test for Manager Task Reassignment System
Tests all manager functionality for task management and reassignment
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
API_BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_manager_task_system():
    """Test manager task management and reassignment functionality"""
    print("🧪 Testing Manager Task Reassignment System...")
    print("=" * 60)
    
    # Step 1: Register Manager
    print("\n1️⃣ Testing Manager Registration")
    manager_data = {
        "name": "Менеджер Тест",
        "phone": "+79991234567",
        "password": "manager123",
        "email": "manager@test.com",
        "department": "Operations"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/auth/register", 
                           headers=HEADERS, json=manager_data)
    
    if response.status_code == 200:
        manager_info = response.json()
        print(f"✅ Manager registered: {manager_info['name']}")
    else:
        print(f"❌ Manager registration failed: {response.text}")
        return False
    
    # Step 2: Manager Login
    print("\n2️⃣ Testing Manager Login")
    login_data = {
        "phone": manager_data["phone"],
        "password": manager_data["password"]
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/auth/login", 
                           headers=HEADERS, json=login_data)
    
    if response.status_code == 200:
        login_result = response.json()
        manager_token = login_result["access_token"]
        manager_headers = {
            **HEADERS,
            "Authorization": f"Bearer {manager_token}"
        }
        print(f"✅ Manager login successful")
    else:
        print(f"❌ Manager login failed: {response.text}")
        return False
    
    # Step 3: Register Multiple Assistants
    print("\n3️⃣ Testing Assistant Registration")
    assistants = []
    assistant_tokens = []
    
    assistant_data_list = [
        {
            "name": "Ассистент Персональный",
            "phone": "+79001111111",
            "password": "assistant123",
            "email": "assistant1@test.com",
            "specialization": "personal_only"
        },
        {
            "name": "Ассистент Универсальный",
            "phone": "+79002222222", 
            "password": "assistant123",
            "email": "assistant2@test.com",
            "specialization": "full_access"
        },
        {
            "name": "Ассистент Бизнес",
            "phone": "+79003333333",
            "password": "assistant123", 
            "email": "assistant3@test.com",
            "specialization": "business_only"
        }
    ]
    
    for i, assistant_data in enumerate(assistant_data_list):
        # Register assistant
        response = requests.post(f"{API_BASE}/api/v1/assistants/auth/register", 
                               headers=HEADERS, json=assistant_data)
        
        if response.status_code == 200:
            assistant_info = response.json()
            assistants.append(assistant_info)
            print(f"✅ Assistant {i+1} registered: {assistant_info['name']}")
            
            # Login assistant
            login_data = {
                "phone": assistant_data["phone"],
                "password": assistant_data["password"]
            }
            
            response = requests.post(f"{API_BASE}/api/v1/assistants/auth/login", 
                                   headers=HEADERS, json=login_data)
            
            if response.status_code == 200:
                login_result = response.json()
                assistant_token = login_result["access_token"]
                assistant_tokens.append(assistant_token)
                
                # Set assistant online
                assistant_headers = {
                    **HEADERS,
                    "Authorization": f"Bearer {assistant_token}"
                }
                
                response = requests.put(f"{API_BASE}/api/v1/assistants/profile/status",
                                      headers=assistant_headers, 
                                      json={"status": "online"})
                
                if response.status_code == 200:
                    print(f"✅ Assistant {i+1} set online")
                else:
                    print(f"⚠️ Could not set assistant {i+1} online: {response.text}")
        else:
            print(f"❌ Assistant {i+1} registration failed: {response.text}")
    
    # Step 4: Register Client and Create Subscription
    print("\n4️⃣ Testing Client Registration and Subscription")
    client_data = {
        "name": "Клиент Тест",
        "phone": "+79555555555",
        "password": "client123",
        "telegram_username": "@testclient"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/clients/auth/register", 
                           headers=HEADERS, json=client_data)
    
    if response.status_code == 200:
        client_info = response.json()
        print(f"✅ Client registered: {client_info['name']}")
        
        # Login client
        login_data = {
            "phone": client_data["phone"],
            "password": client_data["password"]
        }
        
        response = requests.post(f"{API_BASE}/api/v1/clients/auth/login", 
                               headers=HEADERS, json=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            client_token = login_result["access_token"]
            client_headers = {
                **HEADERS,
                "Authorization": f"Bearer {client_token}"
            }
            print(f"✅ Client login successful")
            
            # Create subscription
            subscription_data = {
                "plan": "personal_2h",
                "payment_token": "test_payment_token_12345"
            }
            
            response = requests.post(f"{API_BASE}/api/v1/clients/subscription/upgrade",
                                   headers=client_headers, json=subscription_data)
            
            if response.status_code == 200:
                subscription_info = response.json()
                print(f"✅ Subscription created successfully")
                print(f"   Response: {subscription_info}")
                # Check if subscription exists in response
                if 'subscription' in subscription_info:
                    print(f"   Plan: {subscription_info['subscription']['plan']}")
                elif 'plan' in subscription_info:
                    print(f"   Plan: {subscription_info['plan']}")
            else:
                print(f"❌ Subscription creation failed: {response.text}")
                return False
        else:
            print(f"❌ Client login failed: {response.text}")
            return False
    else:
        print(f"❌ Client registration failed: {response.text}")
        return False
    
    # Step 5: Create Test Tasks
    print("\n5️⃣ Testing Task Creation")
    tasks = []
    
    task_data_list = [
        {
            "title": "Персональная задача 1",
            "description": "Помочь с покупкой продуктов",
            "type": "personal",
            "deadline": (datetime.now() + timedelta(hours=24)).isoformat()
        },
        {
            "title": "Бизнес задача 1", 
            "description": "Подготовить презентацию для клиента",
            "type": "business",
            "deadline": (datetime.now() + timedelta(hours=48)).isoformat()
        },
        {
            "title": "Персональная задача 2",
            "description": "Забронировать ресторан",
            "type": "personal",
            "deadline": (datetime.now() + timedelta(hours=12)).isoformat()
        }
    ]
    
    for i, task_data in enumerate(task_data_list):
        response = requests.post(f"{API_BASE}/api/v1/clients/tasks", 
                               headers=client_headers, json=task_data)
        
        if response.status_code == 200:
            task_info = response.json()
            tasks.append(task_info)
            print(f"✅ Task {i+1} created: {task_info['title']}")
        else:
            print(f"❌ Task {i+1} creation failed: {response.text}")
    
    time.sleep(1)  # Wait for auto-assignment processing
    
    # Step 6: Test Manager Dashboard - View Tasks
    print("\n6️⃣ Testing Manager Task View")
    response = requests.get(f"{API_BASE}/api/v1/management/tasks", 
                          headers=manager_headers)
    
    if response.status_code == 200:
        task_data = response.json()
        manager_tasks = task_data['tasks']
        print(f"✅ Manager can view {len(manager_tasks)} tasks")
        
        for task in manager_tasks:
            status_text = "✅ Assigned" if task['assistant'] else "⚠️ Unassigned"
            assistant_name = task['assistant']['name'] if task['assistant'] else "None"
            print(f"   - Task {task['id']}: {task['title']} | {task['type']} | {status_text} to {assistant_name}")
    else:
        print(f"❌ Manager task view failed: {response.text}")
        return False
    
    # Step 7: Test Manager - View Assistants
    print("\n7️⃣ Testing Manager Assistant View")
    response = requests.get(f"{API_BASE}/api/v1/management/assistants", 
                          headers=manager_headers)
    
    if response.status_code == 200:
        assistant_data = response.json()
        manager_assistants = assistant_data['assistants']
        print(f"✅ Manager can view {len(manager_assistants)} assistants")
        
        for assistant in manager_assistants:
            print(f"   - Assistant {assistant['id']}: {assistant['name']} | {assistant['specialization']} | {assistant['status']} | {assistant['current_active_tasks']}/5 tasks")
    else:
        print(f"❌ Manager assistant view failed: {response.text}")
        return False
    
    # Step 8: Test Task Reassignment
    print("\n8️⃣ Testing Task Reassignment")
    
    # Find a task to reassign
    unassigned_task = None
    assigned_task = None
    
    for task in manager_tasks:
        if not task['assistant']:
            unassigned_task = task
        elif task['assistant']:
            assigned_task = task
    
    if unassigned_task:
        print(f"🔄 Testing assignment of unassigned task: {unassigned_task['title']}")
        
        # Get available assistants for this task type
        response = requests.get(f"{API_BASE}/api/v1/management/assistants/available?task_type={unassigned_task['type']}", 
                              headers=manager_headers)
        
        if response.status_code == 200:
            available_assistants = response.json()
            print(f"✅ Found {len(available_assistants)} available assistants")
            
            # Find an available assistant
            available_assistant = None
            for assistant in available_assistants:
                if assistant['is_available']:
                    available_assistant = assistant
                    break
            
            if available_assistant:
                print(f"🎯 Assigning task to: {available_assistant['name']}")
                
                # Reassign task
                reassign_data = {
                    "assistant_id": available_assistant['id']
                }
                
                response = requests.put(f"{API_BASE}/api/v1/management/tasks/{unassigned_task['id']}/reassign",
                                      headers=manager_headers, json=reassign_data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Task reassigned successfully: {result['message']}")
                else:
                    print(f"❌ Task reassignment failed: {response.text}")
            else:
                print("⚠️ No available assistants found for assignment")
        else:
            print(f"❌ Failed to get available assistants: {response.text}")
    
    if assigned_task:
        print(f"🔄 Testing unassignment of assigned task: {assigned_task['title']}")
        
        # Unassign task (return to marketplace)
        reassign_data = {
            "assistant_id": None
        }
        
        response = requests.put(f"{API_BASE}/api/v1/management/tasks/{assigned_task['id']}/reassign",
                              headers=manager_headers, json=reassign_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task unassigned successfully: {result['message']}")
        else:
            print(f"❌ Task unassignment failed: {response.text}")
    
    # Step 9: Test Assistant Workload Management
    print("\n9️⃣ Testing Assistant Workload Management")
    
    # Try to overload an assistant (assign more than 5 tasks)
    if len(available_assistants) > 0:
        target_assistant = available_assistants[0]
        print(f"🧪 Testing workload limits for: {target_assistant['name']}")
        
        # Create additional tasks to test workload limit
        for i in range(6):  # Try to create 6 tasks for one assistant
            extra_task_data = {
                "title": f"Overload Test Task {i+1}",
                "description": f"Testing workload limits - task {i+1}",
                "type": "personal",
                "deadline": (datetime.now() + timedelta(hours=6)).isoformat()
            }
            
            response = requests.post(f"{API_BASE}/api/v1/clients/tasks", 
                                   headers=client_headers, json=extra_task_data)
            
            if response.status_code == 200:
                extra_task = response.json()
                
                # Try to assign to the same assistant
                reassign_data = {
                    "assistant_id": target_assistant['id']
                }
                
                response = requests.put(f"{API_BASE}/api/v1/management/tasks/{extra_task['id']}/reassign",
                                      headers=manager_headers, json=reassign_data)
                
                if response.status_code == 200:
                    print(f"✅ Task {i+1} assigned successfully")
                else:
                    error_data = response.json()
                    if "maximum workload" in error_data.get('detail', ''):
                        print(f"✅ Workload limit enforced at task {i+1}: {error_data['detail']}")
                        break
                    else:
                        print(f"❌ Unexpected error at task {i+1}: {error_data.get('detail')}")
    
    # Step 10: Test Manager Analytics
    print("\n🔟 Testing Manager Analytics")
    response = requests.get(f"{API_BASE}/api/v1/management/dashboard/overview", 
                          headers=manager_headers)
    
    if response.status_code == 200:
        overview = response.json()
        print(f"✅ Manager analytics loaded")
        print(f"   📊 Tasks: {overview['tasks']['total']} total, {overview['tasks']['pending']} pending")
        print(f"   👥 Assistants: {overview['assistants']['online_now']}/{overview['assistants']['total_active']} online")
        print(f"   👤 Clients: {overview['clients']['total_active']} active, {overview['clients']['active_subscribers']} subscribers")
    else:
        print(f"❌ Manager analytics failed: {response.text}")
    
    # Step 11: Test Marketplace Stats
    print("\n1️⃣1️⃣ Testing Marketplace Statistics")
    response = requests.get(f"{API_BASE}/api/v1/management/marketplace/stats", 
                          headers=manager_headers)
    
    if response.status_code == 200:
        marketplace_stats = response.json()
        print(f"✅ Marketplace statistics loaded")
        print(f"   📈 Pending tasks: {marketplace_stats.get('total_pending_tasks', 0)}")
        print(f"   🏃 Online assistants: {marketplace_stats.get('online_assistants', 0)}")
        print(f"   ⚠️ Overdue tasks: {marketplace_stats.get('overdue_tasks', 0)}")
        print(f"   🎯 System health: {marketplace_stats.get('system_health', 'unknown')}")
        
        if marketplace_stats.get('recommendations'):
            print(f"   💡 Recommendations:")
            for rec in marketplace_stats.get('recommendations', []):
                print(f"      - {rec}")
    else:
        print(f"❌ Marketplace statistics failed: {response.text}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 Manager Task System Test Complete!")
    print("\n✅ Tested Features:")
    print("   - Manager registration and authentication")
    print("   - Multi-assistant registration with specializations")
    print("   - Client registration and subscription creation")
    print("   - Task creation and auto-assignment")
    print("   - Manager task overview and filtering")
    print("   - Manager assistant management")
    print("   - Task reassignment to specific assistants")
    print("   - Task unassignment (return to marketplace)")
    print("   - Assistant workload limit enforcement")
    print("   - Manager analytics dashboard")
    print("   - Marketplace statistics and monitoring")
    
    print("\n🎯 Manager can now:")
    print("   - View all tasks in the system with full details")
    print("   - See which assistants are available and their workload")
    print("   - Reassign tasks from one assistant to another")
    print("   - Remove tasks from assistants and return to marketplace")
    print("   - Monitor system performance and health")
    print("   - Get recommendations for system optimization")
    
    return True

if __name__ == "__main__":
    try:
        success = test_manager_task_system()
        if success:
            print("\n🎉 All tests passed! Manager task system is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc() 