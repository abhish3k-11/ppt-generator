import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_gateway():
    """Test API Gateway functionality"""
    print("🧪 Testing PPT Generator API Gateway...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test detailed health
    try:
        response = requests.get(f"{BASE_URL}/health/detailed")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Detailed health check passed")
            for service, status in health_data.get("dependencies", {}).items():
                print(f"   {service}: {status}")
        else:
            print(f"❌ Detailed health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Detailed health check error: {e}")
    
    # Test user registration
    test_user = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 200:
            print("✅ User registration passed")
            user_data = response.json()
            print(f"   Created user: {user_data['username']}")
        elif response.status_code == 400:
            print("ℹ️  User already exists (expected)")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User registration error: {e}")
    
    # Test user login
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ User login passed")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   Token received: {access_token[:50]}...")
            
            # Test authenticated endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            if response.status_code == 200:
                print("✅ Authenticated request passed")
                user_info = response.json()
                print(f"   User info: {user_info['username']}")
            else:
                print(f"❌ Authenticated request failed: {response.status_code}")
                
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User login error: {e}")
    
    print("\n🎯 Gateway testing completed!")

if __name__ == "__main__":
    # Wait a moment for services to be ready
    print("⏳ Waiting for gateway to be ready...")
    time.sleep(2)
    test_gateway()
