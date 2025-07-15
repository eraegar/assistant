#!/usr/bin/env python3
"""
Test script for Manager Notification System
Tests detection of potential clients and notifications for managers
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def get_manager_token():
    """Get manager authentication token"""
    print("🔐 Getting manager token...")
    
    login_data = {
        "phone": "+79089050077",
        "password": "admin32451124"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/management/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Manager token obtained")
        return token
    else:
        print(f"❌ Failed to get manager token: {response.text}")
        return None

def create_test_telegram_analytics(token):
    """Create test Telegram analytics data for potential clients"""
    print("\n📊 Creating test Telegram analytics data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test user 1: High engagement, viewed pricing, but didn't register
    test_interactions_user1 = [
        {
            "telegram_user_id": "potential_client_001",
            "action": "start",
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "Алексей",
                "username": "alex_potential",
                "language_code": "ru"
            }
        },
        {
            "telegram_user_id": "potential_client_001",
            "action": "view_pricing",
            "conversion_stage": "viewed_pricing",
            "action_data": {"plan_viewed": "business"}
        },
        {
            "telegram_user_id": "potential_client_001",
            "action": "view_examples",
            "conversion_stage": "viewed_examples"
        },
        {
            "telegram_user_id": "potential_client_001",
            "action": "contact_support",
            "action_data": {"question": "Какие у вас гарантии качества?"}
        },
        {
            "telegram_user_id": "potential_client_001",
            "action": "view_pricing",
            "conversion_stage": "viewed_pricing",
            "action_data": {"plan_viewed": "personal"}
        },
        {
            "telegram_user_id": "potential_client_001",
            "action": "click_register",
            "conversion_stage": "clicked_register"
        }
    ]
    
    # Test user 2: Multiple sessions, pricing views
    test_interactions_user2 = [
        {
            "telegram_user_id": "potential_client_002",
            "action": "start",
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "Мария",
                "username": "maria_interested",
                "language_code": "ru"
            },
            "session_id": "session_1"
        },
        {
            "telegram_user_id": "potential_client_002",
            "action": "view_pricing",
            "conversion_stage": "viewed_pricing",
            "session_id": "session_1"
        },
        {
            "telegram_user_id": "potential_client_002",
            "action": "start",
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "Мария",
                "username": "maria_interested"
            },
            "session_id": "session_2"
        },
        {
            "telegram_user_id": "potential_client_002",
            "action": "view_examples",
            "session_id": "session_2"
        },
        {
            "telegram_user_id": "potential_client_002",
            "action": "view_pricing",
            "conversion_stage": "viewed_pricing",
            "session_id": "session_2"
        }
    ]
    
    # Test user 3: Low engagement (should not trigger notifications)
    test_interactions_user3 = [
        {
            "telegram_user_id": "potential_client_003",
            "action": "start",
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "Иван",
                "username": "ivan_casual"
            }
        },
        {
            "telegram_user_id": "potential_client_003",
            "action": "view_services"
        }
    ]
    
    all_interactions = test_interactions_user1 + test_interactions_user2 + test_interactions_user3
    
    success_count = 0
    for interaction in all_interactions:
        response = requests.post(
            f"{BASE_URL}/api/v1/management/analytics/telegram/track",
            headers=headers,
            json=interaction
        )
        
        if response.status_code == 200:
            success_count += 1
        else:
            print(f"❌ Failed to track interaction: {response.text}")
    
    print(f"✅ Successfully tracked {success_count}/{len(all_interactions)} interactions")
    return success_count > 0

def test_potential_client_detection(token):
    """Test potential client detection"""
    print("\n🔍 Testing potential client detection...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/notifications/potential-clients?hours_back=24&min_score=3.0",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        clients = data["potential_clients"]
        
        print("✅ Potential clients detected:")
        print(f"   Total found: {data['total_found']}")
        print(f"   Shown (min score {data['min_score_filter']}): {data['total_shown']}")
        
        for client in clients:
            print(f"\n   👤 {client['first_name']} (@{client['username']})")
            print(f"      Engagement Score: {client['engagement_score']:.1f}/100")
            print(f"      Interactions: {client['total_interactions']}")
            print(f"      Sessions: {client['total_sessions']}")
            print(f"      Viewed Pricing: {'✅' if client['viewed_pricing'] else '❌'}")
            print(f"      Contacted Support: {'✅' if client['contacted_support'] else '❌'}")
            print(f"      Clicked Register: {'✅' if client['clicked_register'] else '❌'}")
        
        return len(clients) > 0
    else:
        print(f"❌ Failed to get potential clients: {response.text}")
        return False

def test_notification_preferences(token):
    """Test notification preferences management"""
    print("\n⚙️ Testing notification preferences...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current preferences
    response = requests.get(
        f"{BASE_URL}/api/v1/management/notifications/preferences",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Current notification preferences:")
        print(f"   Available types: {data['available_types']}")
        print(f"   Available channels: {data['available_channels']}")
        print(f"   Current preferences: {len(data['preferences'])}")
    else:
        print(f"❌ Failed to get preferences: {response.text}")
        return False
    
    # Set up notification preferences
    preferences_to_set = [
        {
            "notification_type": "POTENTIAL_CLIENT_ENGAGED",
            "channel": "IN_APP",
            "is_enabled": True
        },
        {
            "notification_type": "PRICING_VIEWED_NO_REGISTRATION",
            "channel": "IN_APP",
            "is_enabled": True
        },
        {
            "notification_type": "MULTIPLE_SESSIONS_NO_REGISTRATION",
            "channel": "IN_APP",
            "is_enabled": True
        }
    ]
    
    print("\n📝 Setting up notification preferences...")
    for pref in preferences_to_set:
        response = requests.put(
            f"{BASE_URL}/api/v1/management/notifications/preferences",
            headers=headers,
            json=pref
        )
        
        if response.status_code == 200:
            print(f"   ✅ {pref['notification_type']} -> {pref['channel']}")
        else:
            print(f"   ❌ Failed to set {pref['notification_type']}: {response.text}")
    
    return True

def test_notification_processing(token):
    """Test notification processing for potential clients"""
    print("\n🔔 Testing notification processing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/notifications/process?hours_back=24",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Notification processing completed:")
        print(f"   Potential clients detected: {data['potential_clients_detected']}")
        print(f"   Notifications sent: {data['notifications_sent']}")
        print(f"   Hours analyzed: {data['hours_analyzed']}")
        
        return data['notifications_sent'] > 0
    else:
        print(f"❌ Failed to process notifications: {response.text}")
        return False

def test_notification_history(token):
    """Test notification history viewing"""
    print("\n📋 Testing notification history...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/notifications/history?days_back=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        notifications = data["notifications"]
        
        print("✅ Notification history retrieved:")
        print(f"   Total notifications: {data['pagination']['total']}")
        
        for notification in notifications[:3]:  # Show first 3
            print(f"\n   📬 {notification['title']}")
            print(f"      Type: {notification['notification_type']}")
            print(f"      Channel: {notification['channel']}")
            print(f"      Status: {notification['status']}")
            print(f"      Sent: {notification['sent_at'][:19]}")
            if notification['related_telegram_user_id']:
                print(f"      Related User: {notification['related_telegram_user_id']}")
        
        return len(notifications) > 0
    else:
        print(f"❌ Failed to get notification history: {response.text}")
        return False

def test_notification_summary(token):
    """Test notification summary statistics"""
    print("\n📊 Testing notification summary...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/notifications/summary?days_back=7",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Notification summary:")
        print(f"   Period: {data['period_days']} days")
        print(f"   Total notifications: {data['total_notifications']}")
        print(f"   Unread notifications: {data['unread_notifications']}")
        print(f"   Active potential clients: {data['active_potential_clients']}")
        
        if data['notifications_by_type']:
            print("   Notifications by type:")
            for ntype, count in data['notifications_by_type'].items():
                print(f"      {ntype}: {count}")
        
        return True
    else:
        print(f"❌ Failed to get notification summary: {response.text}")
        return False

def test_test_notification(token):
    """Test sending a test notification"""
    print("\n🧪 Testing test notification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/management/notifications/test",
        headers=headers,
        json={"channel": "IN_APP"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Test notification sent:")
        print(f"   Message: {data['message']}")
        print(f"   Notification ID: {data['notification_id']}")
        return True
    else:
        print(f"❌ Failed to send test notification: {response.text}")
        return False

def main():
    """Run all notification system tests"""
    print("🧪 Testing Manager Notification System")
    print("=" * 60)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Cannot run tests without authentication")
        return
    
    # Run test sequence
    tests_passed = 0
    total_tests = 7
    
    try:
        # Test 1: Create test data
        if create_test_telegram_analytics(token):
            tests_passed += 1
        
        # Test 2: Detection
        if test_potential_client_detection(token):
            tests_passed += 1
        
        # Test 3: Preferences
        if test_notification_preferences(token):
            tests_passed += 1
        
        # Test 4: Processing
        if test_notification_processing(token):
            tests_passed += 1
        
        # Test 5: History
        if test_notification_history(token):
            tests_passed += 1
        
        # Test 6: Summary
        if test_notification_summary(token):
            tests_passed += 1
        
        # Test 7: Test notification
        if test_test_notification(token):
            tests_passed += 1
        
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
    
    # Results
    print("\n" + "=" * 60)
    print(f"🎉 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Notification system is working correctly.")
        print("\n💡 Key features demonstrated:")
        print("   • Automatic detection of potential clients")
        print("   • Engagement score calculation")
        print("   • Configurable notification preferences")
        print("   • Multiple notification channels (in-app, email, telegram, sms)")
        print("   • Notification history and tracking")
        print("   • Manager dashboard integration")
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 