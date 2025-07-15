#!/usr/bin/env python3
"""
Test script for subscription management functionality
"""

import requests
import json
from datetime import datetime, timedelta

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

def test_subscription_filters(token):
    """Test subscription filtering functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing subscription filters...")
    
    # Test filter by subscription plan
    response = requests.get(f"{BASE_URL}/api/v1/management/clients?subscription_plan=full_8h", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clients with full_8h plan: {len(data['clients'])}")
        
        # Show applied filters
        filters = data.get('filters', {})
        print(f"   Applied filter: subscription_plan={filters.get('subscription_plan')}")
    else:
        print(f"❌ Failed to filter by subscription plan: {response.text}")
        return False
    
    # Test filter by auto-renewal status
    response = requests.get(f"{BASE_URL}/api/v1/management/clients?auto_renew=true", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clients with auto-renewal enabled: {len(data['clients'])}")
    else:
        print(f"❌ Failed to filter by auto-renewal: {response.text}")
        return False
    
    return True

def test_expiring_subscriptions(token):
    """Test filtering clients with expiring subscriptions"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing expiring subscription filters...")
    
    # Test clients expiring in 30 days
    response = requests.get(f"{BASE_URL}/api/v1/management/clients?expires_in_days=30", headers=headers)
    if response.status_code == 200:
        data = response.json()
        expiring_count = len(data['clients'])
        print(f"✅ Clients expiring in 30 days: {expiring_count}")
        
        # Show subscription details for first few clients
        for client in data['clients'][:3]:
            subscription = client.get('subscription', {})
            expires_at = subscription.get('expires_at', 'Unknown')
            days_left = subscription.get('days_until_expiry', 'Unknown')
            auto_renew = subscription.get('auto_renew', False)
            
            print(f"   - {client['name']}: expires {expires_at[:10] if expires_at != 'Unknown' else expires_at}")
            print(f"     Days left: {days_left}, Auto-renew: {auto_renew}")
    else:
        print(f"❌ Failed to filter expiring subscriptions: {response.text}")
        return False
    
    return True

def test_subscription_alerts(token):
    """Test subscription alerts endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing subscription alerts...")
    
    # Test default alerts (7 days)
    response = requests.get(f"{BASE_URL}/api/v1/management/clients/subscription-alerts", headers=headers)
    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', {})
        
        print(f"✅ Subscription alerts (7 days ahead):")
        print(f"   Expiring: {summary.get('expiring_count', 0)}")
        print(f"   Expired: {summary.get('expired_count', 0)}")
        print(f"   Manual renewals needed: {summary.get('manual_renewal_count', 0)}")
        
        # Show some expiring subscriptions
        expiring = data.get('expiring_subscriptions', [])
        if expiring:
            print(f"   📋 Expiring subscriptions:")
            for client in expiring[:3]:
                subscription = client.get('subscription', {})
                days_left = subscription.get('days_left', 'Unknown')
                plan = subscription.get('plan', 'Unknown')
                print(f"     - {client['name']} ({plan}): {days_left} days left")
        
        # Show expired subscriptions
        expired = data.get('expired_subscriptions', [])
        if expired:
            print(f"   ⚠️  Expired subscriptions:")
            for client in expired[:3]:
                subscription = client.get('subscription', {})
                plan = subscription.get('plan', 'Unknown')
                print(f"     - {client['name']} ({plan}): EXPIRED")
    else:
        print(f"❌ Failed to get subscription alerts: {response.text}")
        return False
    
    return True

def test_client_search(token):
    """Test client search functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing client search...")
    
    # Test search by name
    search_terms = ["Роман", "Иван", "test"]
    
    for term in search_terms:
        response = requests.get(f"{BASE_URL}/api/v1/management/clients", 
                              headers=headers, 
                              params={"search": term, "limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search '{term}': {len(data['clients'])} clients found")
            
            # Show matching clients
            for client in data['clients']:
                subscription = client.get('subscription')
                if subscription:
                    plan = subscription.get('plan', 'No plan')
                    expires_info = subscription.get('days_until_expiry', 'Unknown')
                    if expires_info != 'Unknown':
                        expires_info = f"{expires_info} days left"
                    print(f"   - {client['name']} ({plan}, {expires_info})")
                else:
                    print(f"   - {client['name']} (No subscription)")
        else:
            print(f"❌ Failed to search for '{term}': {response.text}")
            return False
    
    return True

def test_subscription_sorting(token):
    """Test subscription-based sorting"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing subscription sorting...")
    
    # Test sort by expiration date (earliest first)
    response = requests.get(f"{BASE_URL}/api/v1/management/clients", 
                          headers=headers, 
                          params={"sort_by": "expires_at", "sort_order": "asc", "limit": 5})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sorted by earliest expiration: {len(data['clients'])} clients")
        
        # Show expiration dates
        for client in data['clients']:
            subscription = client.get('subscription')
            if subscription:
                expires_at = subscription.get('expires_at', 'No expiry')
                days_left = subscription.get('days_until_expiry', 'Unknown')
                is_expiring = subscription.get('is_expiring_soon', False)
                
                status_icon = "⚠️" if is_expiring else "✅"
                expires_date = expires_at[:10] if expires_at != 'No expiry' else expires_at
                
                print(f"   {status_icon} {client['name']}: expires {expires_date} ({days_left} days)")
    else:
        print(f"❌ Failed to sort by expiration: {response.text}")
        return False
    
    return True

def test_combined_subscription_filters(token):
    """Test combination of subscription filters"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing combined subscription filters...")
    
    # Test complex filter: clients with business plans, auto-renewal disabled, expiring in 14 days
    params = {
        "subscription_plan": "business_8h",
        "auto_renew": "false", 
        "expires_in_days": "14",
        "sort_by": "expires_at",
        "sort_order": "asc"
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/management/clients", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Combined subscription filter: {len(data['clients'])} clients")
        print(f"   Filter: Business plan + No auto-renewal + Expiring in 14 days")
        
        # Show applied filters
        filters = data.get('filters', {})
        active_filters = [f"{k}={v}" for k, v in filters.items() if v is not None]
        print(f"   Applied: {', '.join(active_filters)}")
        
        # Show results
        for client in data['clients']:
            subscription = client['subscription'] if client['subscription'] else {}
            plan = subscription.get('plan', 'No plan')
            auto_renew = subscription.get('auto_renew', 'Unknown')
            days_left = subscription.get('days_until_expiry', 'Unknown')
            
            print(f"   - {client['name']}: {plan}, Auto-renew: {auto_renew}, Days left: {days_left}")
    else:
        print(f"❌ Failed to apply combined filters: {response.text}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Subscription Management System")
    print("=" * 50)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Manager authenticated successfully\n")
    
    # Run all tests
    tests = [
        ("Subscription Filters", test_subscription_filters),
        ("Expiring Subscriptions", test_expiring_subscriptions),
        ("Subscription Alerts", test_subscription_alerts),
        ("Client Search", test_client_search),
        ("Subscription Sorting", test_subscription_sorting),
        ("Combined Filters", test_combined_subscription_filters)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func(token):
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All subscription management tests completed successfully!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main() 