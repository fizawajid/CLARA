"""
Simple script to test API connection
Run this to verify the API is working
"""

import httpx
import json

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Testing CLARA NLP API")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint (GET /)...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Health endpoint
    print("\n2. Testing health endpoint (GET /health)...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Info endpoint
    print("\n3. Testing info endpoint (GET /info)...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/info")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   API Title: {data.get('api', {}).get('title')}")
            print(f"   API Version: {data.get('api', {}).get('version')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Statistics endpoint
    print("\n4. Testing statistics endpoint (GET /api/v1/statistics)...")
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{base_url}/api/v1/statistics")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All API tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_api()
    if not success:
        print("\n⚠️ API tests failed. Check if the API server is running:")
        print("   python -m uvicorn src.api.main:app --reload")