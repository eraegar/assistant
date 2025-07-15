import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Тестирование API...")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test 3: API info
    try:
        response = requests.get(f"{base_url}/api/v1/info")
        print(f"✅ Info endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Info endpoint failed: {e}")
    
    # Test 4: Client registration endpoint exists
    try:
        response = requests.post(f"{base_url}/api/v1/clients/auth/register", 
                               json={"test": "endpoint_check"})
        print(f"✅ Client register endpoint responds: {response.status_code}")
    except Exception as e:
        print(f"❌ Client register endpoint failed: {e}")

if __name__ == "__main__":
    test_api() 