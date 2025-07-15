#!/usr/bin/env python3
"""
Test script for enhanced task filtering functionality
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

def test_basic_filters(token):
    """Test basic filtering functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing basic task filters...")
    
    # Test status filter
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks?status=completed", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Completed tasks: {len(data['tasks'])}")
        print(f"   Applied filters: {data['filters']['status']}")
    else:
        print(f"❌ Failed to filter by status: {response.text}")
        return False
    
    # Test task type filter
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks?task_type=personal", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Personal tasks: {len(data['tasks'])}")
    else:
        print(f"❌ Failed to filter by task type: {response.text}")
        return False
    
    return True

def test_search_filter(token):
    """Test search functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing search filter...")
    
    # Test search in title and description
    search_terms = ["найти", "купить", "забронировать"]
    
    for term in search_terms:
        response = requests.get(f"{BASE_URL}/api/v1/management/tasks", 
                              headers=headers, 
                              params={"search": term, "limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search '{term}': {len(data['tasks'])} tasks found")
            
            # Show matching tasks
            for task in data['tasks'][:2]:  # Show first 2 results
                print(f"   - '{task['title']}' (ID: {task['id']})")
        else:
            print(f"❌ Failed to search for '{term}': {response.text}")
            return False
    
    return True

def test_rating_filter(token):
    """Test rating-based filtering"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing rating filters...")
    
    # Test tasks with ratings
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks?has_rating=true", headers=headers)
    if response.status_code == 200:
        data = response.json()
        rated_count = len(data['tasks'])
        print(f"✅ Tasks with ratings: {rated_count}")
        
        # Show some rated tasks
        for task in data['tasks'][:3]:
            if task['client_rating']:
                print(f"   - '{task['title']}' - ★{task['client_rating']}")
    else:
        print(f"❌ Failed to filter rated tasks: {response.text}")
        return False
    
    # Test tasks without ratings
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks?has_rating=false", headers=headers)
    if response.status_code == 200:
        data = response.json()
        unrated_count = len(data['tasks'])
        print(f"✅ Tasks without ratings: {unrated_count}")
    else:
        print(f"❌ Failed to filter unrated tasks: {response.text}")
        return False
    
    return True

def test_sorting(token):
    """Test sorting functionality"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing sorting options...")
    
    sort_tests = [
        ("created_at", "desc", "Newest first"),
        ("created_at", "asc", "Oldest first"),
        ("client_rating", "desc", "Highest rated first"),
        ("deadline", "asc", "Earliest deadline first")
    ]
    
    for sort_by, sort_order, description in sort_tests:
        response = requests.get(f"{BASE_URL}/api/v1/management/tasks", 
                              headers=headers, 
                              params={"sort_by": sort_by, "sort_order": sort_order, "limit": 3})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: {len(data['tasks'])} tasks")
            
            # Show first task as example
            if data['tasks']:
                task = data['tasks'][0]
                sort_value = task.get(sort_by, "N/A")
                if sort_by == "created_at" and sort_value != "N/A":
                    sort_value = sort_value[:19]  # Trim to readable format
                print(f"   Example: '{task['title']}' ({sort_by}: {sort_value})")
        else:
            print(f"❌ Failed to sort by {sort_by}: {response.text}")
            return False
    
    return True

def test_overdue_filter(token):
    """Test overdue task filtering"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing overdue filter...")
    
    # Test overdue tasks
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks?is_overdue=true", headers=headers)
    if response.status_code == 200:
        data = response.json()
        overdue_count = len(data['tasks'])
        print(f"✅ Overdue tasks: {overdue_count}")
        
        # Show overdue tasks
        for task in data['tasks'][:3]:
            deadline = task.get('deadline', 'No deadline')
            if deadline != 'No deadline':
                deadline = deadline[:19]  # Trim to readable format
            print(f"   - '{task['title']}' (Deadline: {deadline}, Status: {task['status']})")
    else:
        print(f"❌ Failed to filter overdue tasks: {response.text}")
        return False
    
    return True

def test_date_range_filter(token):
    """Test date range filtering"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing date range filters...")
    
    # Test last 7 days
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    now = datetime.utcnow().isoformat()
    
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks", 
                          headers=headers, 
                          params={"date_from": week_ago, "date_to": now})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Tasks from last 7 days: {len(data['tasks'])}")
        print(f"   Date range: {week_ago[:10]} to {now[:10]}")
    else:
        print(f"❌ Failed to filter by date range: {response.text}")
        return False
    
    return True

def test_combined_filters(token):
    """Test combination of multiple filters"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔄 Testing combined filters...")
    
    # Test complex filter: completed personal tasks with ratings, sorted by rating
    params = {
        "status": "completed",
        "task_type": "personal", 
        "has_rating": "true",
        "sort_by": "client_rating",
        "sort_order": "desc",
        "limit": 5
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/management/tasks", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Combined filter result: {len(data['tasks'])} tasks")
        print(f"   Filters: Completed + Personal + Rated + Sorted by rating")
        
        # Show applied filters
        filters = data.get('filters', {})
        active_filters = [f"{k}={v}" for k, v in filters.items() if v is not None]
        print(f"   Applied: {', '.join(active_filters)}")
        
        # Show results
        for task in data['tasks']:
            rating = task.get('client_rating', 'No rating')
            print(f"   - '{task['title']}' (★{rating}, {task['type']})")
    else:
        print(f"❌ Failed to apply combined filters: {response.text}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Testing Enhanced Task Filtering System")
    print("=" * 50)
    
    # Get authentication token
    token = get_manager_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Manager authenticated successfully\n")
    
    # Run all tests
    tests = [
        ("Basic Filters", test_basic_filters),
        ("Search Filter", test_search_filter),
        ("Rating Filter", test_rating_filter),
        ("Sorting Options", test_sorting),
        ("Overdue Filter", test_overdue_filter),
        ("Date Range Filter", test_date_range_filter),
        ("Combined Filters", test_combined_filters)
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
        print("🎉 All filtering tests completed successfully!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main() 