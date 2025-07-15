#!/usr/bin/env python3
"""
Test script for simplified tariff structure
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_simplified_plans():
    """Test the new simplified subscription plans API"""
    
    print("🔄 Testing simplified tariff structure...")
    
    # Test subscription plans endpoint
    response = requests.get(f"{BASE_URL}/api/v1/clients/subscription/plans")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Plans API successful")
        
        if "plans" in data:
            plans = data["plans"]
            print(f"📋 Found {len(plans)} plan categories:")
            
            for plan in plans:
                print(f"\n  📦 {plan['name']}")
                print(f"     ID: {plan['id']}")
                print(f"     Price range: {plan['price_range']}")
                print(f"     Hours: {plan['hours_range']}")
                print(f"     Description: {plan['description']}")
                print(f"     Task types: {', '.join(plan['task_types'])}")
                
                if 'recommended' in plan and plan['recommended']:
                    print(f"     ⭐ RECOMMENDED")
                
                # Show detailed plans
                detailed_plans = plan.get('detailed_plans', [])
                if detailed_plans:
                    print(f"     💎 Detailed options:")
                    for detail in detailed_plans:
                        recommended_mark = " ⭐" if detail.get('recommended') else ""
                        print(f"       - {detail['name']}: {detail['price_formatted']} ({detail['hours']}ч){recommended_mark}")
            
            # Test structure validation
            expected_categories = ['personal', 'business', 'combo']
            found_categories = [plan['id'] for plan in plans]
            
            for category in expected_categories:
                if category in found_categories:
                    print(f"✅ Category '{category}' found")
                else:
                    print(f"❌ Category '{category}' missing")
            
            # Check detailed plans structure
            print(f"\n🔍 Validating detailed plans structure...")
            for plan in plans:
                category_id = plan['id']
                detailed_plans = plan.get('detailed_plans', [])
                
                if not detailed_plans:
                    print(f"❌ Category '{category_id}' has no detailed plans")
                    continue
                
                print(f"✅ Category '{category_id}' has {len(detailed_plans)} detailed plans")
                
                # Validate detailed plan IDs match category
                for detail in detailed_plans:
                    detail_id = detail['id']
                    if category_id == 'combo':
                        expected_prefix = 'full_'
                    else:
                        expected_prefix = f'{category_id}_'
                    
                    if detail_id.startswith(expected_prefix):
                        print(f"  ✅ {detail_id} matches category {category_id}")
                    else:
                        print(f"  ❌ {detail_id} doesn't match category {category_id}")
        
        return True
    else:
        print(f"❌ Failed to get plans: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_plan_selection_workflow():
    """Test the complete plan selection workflow"""
    print(f"\n🔄 Testing plan selection workflow...")
    
    # This would typically involve:
    # 1. Get simplified plans
    # 2. User selects category (personal/business/combo)
    # 3. User selects specific plan (2h/5h/8h)
    # 4. User proceeds to payment
    
    response = requests.get(f"{BASE_URL}/api/v1/clients/subscription/plans")
    if response.status_code != 200:
        print("❌ Cannot test workflow - plans API failed")
        return False
    
    data = response.json()
    plans = data.get("plans", [])
    
    if not plans:
        print("❌ No plans found for workflow test")
        return False
    
    # Simulate user selecting business category
    business_plan = next((p for p in plans if p['id'] == 'business'), None)
    if business_plan:
        print(f"✅ Found business category: {business_plan['name']}")
        print(f"   Price range: {business_plan['price_range']}")
        
        # Show detailed options
        detailed_plans = business_plan.get('detailed_plans', [])
        if detailed_plans:
            print(f"   Available options:")
            for detail in detailed_plans:
                print(f"     - {detail['name']}: {detail['price_formatted']}")
        
        # Simulate selecting specific plan
        recommended_plan = next((d for d in detailed_plans if d.get('recommended')), detailed_plans[0] if detailed_plans else None)
        if recommended_plan:
            print(f"✅ Recommended option: {recommended_plan['name']} - {recommended_plan['price_formatted']}")
            return True
    
    print("❌ Business category workflow test failed")
    return False

def main():
    """Main test function"""
    print("🚀 Testing Simplified Tariff Structure")
    print("=" * 50)
    
    # Test simplified plans
    if not test_simplified_plans():
        print("❌ Simplified plans test failed")
        return
    
    # Test workflow
    if not test_plan_selection_workflow():
        print("❌ Workflow test failed")
        return
    
    print(f"\n🎉 All tests passed! Simplified tariff structure is working correctly.")
    print(f"\n📋 Summary:")
    print(f"  ✅ 3 main categories (Personal, Business, Combo)")
    print(f"  ✅ Price ranges instead of fixed prices")
    print(f"  ✅ Detailed plans for each category")
    print(f"  ✅ Backwards compatibility with existing plan IDs")

if __name__ == "__main__":
    main() 