#!/usr/bin/env python3
"""
Test script for Telegram Bot Analytics
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

def test_telegram_analytics(token):
    """Test Telegram analytics endpoints"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Testing Telegram Analytics...")
    print("=" * 50)
    
    # Test 1: Create some test analytics data
    print("🔄 Creating test analytics data...")
    
    test_interactions = [
        {
            "telegram_user_id": "123456789",
            "action": "start", 
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "TestUser",
                "username": "testuser"
            }
        },
        {
            "telegram_user_id": "123456789",
            "action": "view_pricing",
            "conversion_stage": "viewed_pricing",
            "action_data": {"source": "bot_menu"}
        },
        {
            "telegram_user_id": "123456789", 
            "action": "view_examples",
            "conversion_stage": "viewed_examples"
        },
        {
            "telegram_user_id": "987654321",
            "action": "start",
            "conversion_stage": "started_bot",
            "user_info": {
                "first_name": "AnotherUser",
                "username": "anotheruser"
            }
        },
        {
            "telegram_user_id": "987654321",
            "action": "contact_support"
        }
    ]
    
    for interaction in test_interactions:
        response = requests.post(
            f"{BASE_URL}/api/v1/management/analytics/telegram/track",
            headers=headers,
            json=interaction
        )
        
        if response.status_code == 200:
            print(f"✅ Tracked: {interaction['action']}")
        else:
            print(f"❌ Failed to track {interaction['action']}: {response.text}")
    
    # Test 2: Get analytics summary
    print("\n📊 Testing analytics summary...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/analytics/telegram/summary?days=7",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Analytics Summary:")
        print(f"   Total interactions: {data['total_interactions']}")
        print(f"   Unique users: {data['unique_users']}")
        print(f"   New users: {data['new_users']}")
        print(f"   Conversion rate: {data['conversion_rate']}%")
        print(f"   Popular actions: {[action['action'] for action in data['popular_actions'][:3]]}")
    else:
        print(f"❌ Failed to get analytics summary: {response.text}")
    
    # Test 3: Get conversion funnel
    print("\n🔄 Testing conversion funnel...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/analytics/telegram/conversion-funnel?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Conversion Funnel:")
        for stage, stats in data["funnel_stats"].items():
            print(f"   {stage}: {stats['unique_users']} users ({stats['total_events']} events)")
        
        print("\n   Conversion Rates:")
        for rate_name, rate_value in data["conversion_rates"].items():
            print(f"   {rate_name}: {rate_value}%")
    else:
        print(f"❌ Failed to get conversion funnel: {response.text}")
    
    # Test 4: Get engagement insights
    print("\n💡 Testing engagement insights...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/analytics/telegram/engagement?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ Engagement Insights:")
        print(f"   Unregistered engaged users: {data['unregistered_engaged_users']}")
        print(f"   Pricing viewers (not registered): {data['pricing_viewers_not_registered']}")
        print(f"   Average interactions per user: {data['avg_interactions_per_user']}")
        
        # Show hourly distribution
        hourly = data.get('hourly_distribution', [])
        if hourly:
            top_hours = sorted(hourly, key=lambda x: x['count'], reverse=True)[:3]
            print(f"   Most active hours: {[(h['hour'], h['count']) for h in top_hours]}")
    else:
        print(f"❌ Failed to get engagement insights: {response.text}")
    
    # Test 5: Get user journey
    print("\n🗺️  Testing user journey...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/analytics/telegram/user-journey/123456789?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✅ User Journey:")
        print(f"   Total interactions: {data['total_interactions']}")
        
        for i, interaction in enumerate(data['journey'][:5], 1):  # Show first 5
            timestamp = interaction['timestamp'][:19]  # Remove microseconds
            print(f"   {i}. {interaction['action']} at {timestamp}")
            if interaction.get('conversion_stage'):
                print(f"      Stage: {interaction['conversion_stage']}")
        
        if len(data['journey']) > 5:
            print(f"   ... and {len(data['journey']) - 5} more interactions")
    else:
        print(f"❌ Failed to get user journey: {response.text}")

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Bot Analytics")
    print("=" * 50)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Cannot run tests without authentication")
        return
    
    # Run analytics tests
    test_telegram_analytics(token)
    
    print("\n🎉 Telegram Analytics Testing Complete!")
    print("💡 This demonstrates tracking bot interactions for conversion analysis")

if __name__ == "__main__":
    main() 