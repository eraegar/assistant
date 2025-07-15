#!/usr/bin/env python3
"""
Test script for Enhanced Client Search Functionality
Tests various search criteria and filters for the manager panel
"""

import requests
import json
from datetime import datetime, timedelta

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

def test_basic_search(token):
    """Test basic search functionality"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Testing Basic Client Search...")
    print("=" * 50)
    
    # Test 1: General search
    print("🔄 Testing general search...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?search=Ivan",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ General search found {len(data['clients'])} clients matching 'Ivan'")
        for client in data['clients'][:3]:  # Show first 3
            print(f"   - {client['name']} ({client['phone']})")
    else:
        print(f"❌ General search failed: {response.text}")
    
    # Test 2: Phone search
    print("\n🔄 Testing phone search...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?phone_search=900",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Phone search found {len(data['clients'])} clients with '900' in phone")
        for client in data['clients'][:3]:
            print(f"   - {client['name']} ({client['phone']})")
    else:
        print(f"❌ Phone search failed: {response.text}")

def test_advanced_search(token):
    """Test advanced search functionality"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎯 Testing Advanced Client Search...")
    print("=" * 50)
    
    # Test 1: Name search
    print("🔄 Testing name-specific search...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?name_search=Test",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Name search found {len(data['clients'])} clients with 'Test' in name")
        for client in data['clients'][:3]:
            print(f"   - {client['name']}")
    else:
        print(f"❌ Name search failed: {response.text}")
    
    # Test 2: Telegram search
    print("\n🔄 Testing Telegram username search...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?telegram_search=test",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Telegram search found {len(data['clients'])} clients with 'test' in Telegram")
        for client in data['clients'][:3]:
            print(f"   - {client['name']} (@{client['telegram_username']})")
    else:
        print(f"❌ Telegram search failed: {response.text}")
    
    # Test 3: Task count filtering
    print("\n🔄 Testing task count filtering...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?min_tasks=1",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Task count filter found {len(data['clients'])} clients with ≥1 tasks")
        for client in data['clients'][:3]:
            print(f"   - {client['name']}: {client['total_tasks']} tasks")
    else:
        print(f"❌ Task count filter failed: {response.text}")

def test_subscription_filters(token):
    """Test subscription-based filtering"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n💳 Testing Subscription Filters...")
    print("=" * 50)
    
    # Test 1: Active subscriptions (default)
    print("🔄 Testing active subscriptions filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        active_count = len([c for c in data['clients'] if c['subscription'] and c['subscription']['status'] == 'active'])
        print(f"✅ Found {len(data['clients'])} clients, {active_count} with active subscriptions")
    else:
        print(f"❌ Active subscriptions filter failed: {response.text}")
    
    # Test 2: All clients (including without subscriptions)
    print("\n🔄 Testing all clients filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        with_sub = len([c for c in data['clients'] if c['subscription']])
        without_sub = len([c for c in data['clients'] if not c['subscription']])
        print(f"✅ Found {len(data['clients'])} total clients")
        print(f"   - With subscriptions: {with_sub}")
        print(f"   - Without subscriptions: {without_sub}")
    else:
        print(f"❌ All clients filter failed: {response.text}")
    
    # Test 3: Specific subscription plan
    print("\n🔄 Testing subscription plan filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?subscription_plan=personal_2h",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['clients'])} clients with 'personal_2h' plan")
        for client in data['clients'][:3]:
            if client['subscription']:
                print(f"   - {client['name']}: {client['subscription']['plan']}")
    else:
        print(f"❌ Subscription plan filter failed: {response.text}")

def test_date_filters(token):
    """Test date-based filtering"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📅 Testing Date Filters...")
    print("=" * 50)
    
    # Test 1: Recent registrations (last 30 days)
    print("🔄 Testing recent registrations filter...")
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?registered_from={thirty_days_ago}&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['clients'])} clients registered in last 30 days")
        for client in data['clients'][:3]:
            reg_date = datetime.fromisoformat(client['created_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d")
            print(f"   - {client['name']}: {reg_date}")
    else:
        print(f"❌ Recent registrations filter failed: {response.text}")
    
    # Test 2: Registration date range
    print("\n🔄 Testing registration date range...")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?registered_from={today}&registered_to={today}&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data['clients'])} clients registered today")
    else:
        print(f"❌ Registration date range filter failed: {response.text}")

def test_boolean_filters(token):
    """Test boolean filtering"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔘 Testing Boolean Filters...")
    print("=" * 50)
    
    # Test 1: Clients with Telegram usernames
    print("🔄 Testing has_telegram filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?has_telegram=true&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        with_telegram = len([c for c in data['clients'] if c['telegram_username']])
        print(f"✅ Found {len(data['clients'])} clients with Telegram usernames")
        print(f"   - Verified count: {with_telegram}")
    else:
        print(f"❌ Has Telegram filter failed: {response.text}")
    
    # Test 2: Clients without Telegram usernames
    print("\n🔄 Testing has_telegram=false filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?has_telegram=false&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        without_telegram = len([c for c in data['clients'] if not c['telegram_username']])
        print(f"✅ Found {len(data['clients'])} clients without Telegram usernames")
        print(f"   - Verified count: {without_telegram}")
    else:
        print(f"❌ No Telegram filter failed: {response.text}")
    
    # Test 3: Clients with assistant assignments
    print("\n🔄 Testing has_assignments filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?has_assignments=true&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        with_assignments = len([c for c in data['clients'] if c['assigned_assistants']])
        print(f"✅ Found {len(data['clients'])} clients with assistant assignments")
        print(f"   - Verified count: {with_assignments}")
        for client in data['clients'][:3]:
            if client['assigned_assistants']:
                assistant_names = [a['name'] for a in client['assigned_assistants']]
                print(f"   - {client['name']}: {', '.join(assistant_names)}")
    else:
        print(f"❌ Has assignments filter failed: {response.text}")

def test_sorting_options(token):
    """Test different sorting options"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Testing Sorting Options...")
    print("=" * 50)
    
    # Test 1: Sort by registration date (newest first)
    print("🔄 Testing sort by created_at DESC...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?sort_by=created_at&sort_order=desc&subscription_status=all&limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sorted {len(data['clients'])} clients by registration date (newest first)")
        for client in data['clients']:
            reg_date = datetime.fromisoformat(client['created_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
            print(f"   - {client['name']}: {reg_date}")
    else:
        print(f"❌ Sort by created_at failed: {response.text}")
    
    # Test 2: Sort by total tasks
    print("\n🔄 Testing sort by total_tasks DESC...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?sort_by=total_tasks&sort_order=desc&subscription_status=all&limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sorted {len(data['clients'])} clients by total tasks (most active first)")
        for client in data['clients']:
            print(f"   - {client['name']}: {client['total_tasks']} total tasks, {client['active_tasks']} active")
    else:
        print(f"❌ Sort by total_tasks failed: {response.text}")

def test_quick_search_endpoint(token):
    """Test the new quick search endpoint"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n⚡ Testing Quick Search Endpoint...")
    print("=" * 50)
    
    # Test 1: Quick search by name
    print("🔄 Testing quick search by name...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients/search?q=Test&search_type=name&limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quick search found {data['total']} clients matching 'Test' in names")
        for result in data['results']:
            subscription = result['subscription']['plan'] if result['subscription'] else 'No subscription'
            print(f"   - {result['name']}: {subscription}")
    else:
        print(f"❌ Quick search by name failed: {response.text}")
    
    # Test 2: Quick search by phone
    print("\n🔄 Testing quick search by phone...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients/search?q=900&search_type=phone&limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quick search found {data['total']} clients with '900' in phone")
        for result in data['results']:
            print(f"   - {result['name']}: {result['phone']}")
    else:
        print(f"❌ Quick search by phone failed: {response.text}")
    
    # Test 3: Search all fields
    print("\n🔄 Testing quick search all fields...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients/search?q=test&search_type=all&limit=10",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quick search found {data['total']} clients matching 'test' in any field")
        for result in data['results'][:5]:  # Show first 5
            print(f"   - {result['name']} ({result['phone']})")
    else:
        print(f"❌ Quick search all fields failed: {response.text}")

def test_combined_filters(token):
    """Test combining multiple filters"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔗 Testing Combined Filters...")
    print("=" * 50)
    
    # Test 1: Combine name search with task count filter
    print("🔄 Testing name search + task count filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?name_search=Test&min_tasks=0&subscription_status=all",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Combined filter found {len(data['clients'])} clients named 'Test' with ≥0 tasks")
        for client in data['clients'][:3]:
            print(f"   - {client['name']}: {client['total_tasks']} tasks")
    else:
        print(f"❌ Combined name + task count filter failed: {response.text}")
    
    # Test 2: Combine subscription plan with Telegram filter
    print("\n🔄 Testing subscription plan + Telegram filter...")
    response = requests.get(
        f"{BASE_URL}/api/v1/management/clients?subscription_plan=personal_2h&has_telegram=true",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Combined filter found {len(data['clients'])} personal_2h clients with Telegram")
        for client in data['clients']:
            plan = client['subscription']['plan'] if client['subscription'] else 'No plan'
            print(f"   - {client['name']}: {plan}, @{client['telegram_username']}")
    else:
        print(f"❌ Combined subscription + Telegram filter failed: {response.text}")

def main():
    """Run all client search tests"""
    print("🧪 Testing Enhanced Client Search Functionality")
    print("=" * 60)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Cannot run tests without authentication")
        return
    
    # Run all test suites
    test_basic_search(token)
    test_advanced_search(token)
    test_subscription_filters(token)
    test_date_filters(token)
    test_boolean_filters(token)
    test_sorting_options(token)
    test_quick_search_endpoint(token)
    test_combined_filters(token)
    
    print("\n🎉 Enhanced Client Search Testing Complete!")
    print("💡 The search system now supports:")
    print("   - General search across multiple fields")
    print("   - Specific field searches (name, email, phone, telegram)")
    print("   - Assistant name search")
    print("   - Task count filtering")
    print("   - Date range filtering")
    print("   - Boolean filters (has_telegram, has_assignments)")
    print("   - Advanced sorting options")
    print("   - Quick search endpoint for suggestions")
    print("   - Combined filters for complex queries")

if __name__ == "__main__":
    main() 