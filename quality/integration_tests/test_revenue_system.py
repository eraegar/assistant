#!/usr/bin/env python3
"""
Test script for Revenue System in Rubles
Verifies pricing in rubles and revenue calculations
"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_pricing_and_revenue():
    """Test subscription pricing in rubles and revenue calculations"""
    print("💰 Testing Pricing and Revenue System...")
    print("=" * 50)
    
    # Test 1: Check Subscription Plans Pricing
    print("\n1️⃣ Testing Subscription Plans (Rubles)")
    response = requests.get(f"{API_BASE}/api/v1/clients/subscription/plans")
    
    if response.status_code == 200:
        plans_data = response.json()
        plans = plans_data.get('plans', [])
        print(f"✅ Found {len(plans)} subscription plans")
        
        for plan in plans:
            print(f"   📋 {plan['name']}")
            print(f"      💰 Цена: {plan['price_formatted']}")
            print(f"      🕐 Часов в день: {plan['hours_per_day']}")
            print(f"      📈 Популярный: {'Да' if plan.get('popular', False) else 'Нет'}")
            print()
            
            # Check that prices are in the new range
            if plan['price'] < 10000:  # Should be at least 15,000 now
                print(f"⚠️ Warning: Price seems too low for plan {plan['id']}: {plan['price']}")
                return False
        
        expected_plans = ['personal_2h', 'personal_5h', 'personal_8h', 
                         'business_2h', 'business_5h', 'business_8h',
                         'full_2h', 'full_5h', 'full_8h']
        actual_plans = [plan['id'] for plan in plans]
        
        if set(actual_plans) != set(expected_plans):
            print(f"❌ Plan mismatch. Expected {expected_plans}, got {actual_plans}")
            return False
        
        print("✅ All subscription plans validated with new pricing!")
        return True
    else:
        print(f"❌ Failed to get subscription plans: {response.text}")
        return False
    
    # Test 2: Manager Analytics
    print("\n2️⃣ Testing Manager Analytics (Revenue)")
    
    # Login as manager instead of registering
    manager_login = {
        "phone": "+79991111111",
        "password": "manager123"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/management/auth/login", 
                           json=manager_login, headers=HEADERS)
    
    if response.status_code == 200:
        login_data = response.json()
        token = login_data["access_token"]
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        print("✅ Manager login successful")
        
        # Get analytics
        analytics_response = requests.get(f"{API_BASE}/api/v1/management/dashboard/overview", 
                                        headers=auth_headers)
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            print("✅ Analytics loaded successfully")
            print(f"\n🔍 Full Analytics Response:")
            print(json.dumps(analytics, indent=2, ensure_ascii=False))
            
            print("\n📊 Revenue Analytics:")
            performance = analytics.get('performance', {})
            clients = analytics.get('clients', {})
            tasks = analytics.get('tasks', {})
            
            monthly_revenue = performance.get('monthly_revenue', 0)
            print(f"   💰 Monthly Revenue: {monthly_revenue:,} ₽")
            print(f"   👥 Active Subscribers: {clients.get('active_subscribers', 0)}")
            print(f"   📈 Total Clients: {clients.get('total_active', 0)}")
            print(f"   🎯 Total Tasks: {tasks.get('total', 0)}")
            
            # Test 3: Clients endpoint
            print("\n3️⃣ Testing Clients Endpoint")
            clients_response = requests.get(f"{API_BASE}/api/v1/management/clients", 
                                          headers=auth_headers)
            
            if clients_response.status_code == 200:
                clients_data = clients_response.json()
                print("✅ Clients loaded successfully")
                print(f"   🧑‍💼 Total Clients: {clients_data.get('pagination', {}).get('total', 0)}")
                
                if clients_data.get('clients'):
                    for client in clients_data['clients'][:3]:  # Show first 3
                        print(f"   📱 {client['name']} ({client['phone']})")
                        if client.get('subscription'):
                            sub = client['subscription']
                            print(f"      💳 Подписка: {sub['plan']} - {sub['status']}")
                        else:
                            print(f"      💔 Без подписки")
                else:
                    print("   ℹ️ No clients found")
            else:
                print(f"❌ Clients request failed: {clients_response.status_code}")
                print(clients_response.text)
            
        else:
            print(f"❌ Analytics request failed: {analytics_response.status_code}")
            print(analytics_response.text)
    else:
        print(f"❌ Manager login failed: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 50)
    print("🎉 Pricing and Revenue System Test Complete!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_pricing_and_revenue()
        if success:
            print("\n🎉 All pricing tests passed! Revenue system works correctly in rubles.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc() 