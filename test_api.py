#!/usr/bin/env python3
"""
Test script to verify FlyerFlutter API functionality in Docker
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_api_status():
    """Test the API status endpoint"""
    print("\nTesting API status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_stores_endpoint():
    """Test the stores endpoint with Toronto coordinates"""
    print("\nTesting stores endpoint (Toronto)...")
    params = {
        "lat": 43.6532,
        "lng": -79.3832,
        "radius": 5000,
        "max_results": 10
    }
    try:
        response = requests.get(f"{BASE_URL}/api/stores", params=params)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total stores found: {data.get('total', 0)}")
        if data.get('stores'):
            print("   First 3 stores:")
            for store in data['stores'][:3]:
                print(f"     - {store.get('name')} ({store.get('address')})")
        else:
            print("   WARNING: No stores returned (may be DNS/API issue)")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_deals_endpoint():
    """Test the deals endpoint"""
    print("\nTesting deals endpoint...")
    params = {
        "page": 1,
        "per_page": 10
    }
    try:
        response = requests.get(f"{BASE_URL}/api/deals", params=params)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total deals found: {data.get('total', 0)}")
        if data.get('deals'):
            print("   First 3 deals:")
            for deal in data['deals'][:3]:
                print(f"     - {deal.get('title')} at {deal.get('store_name')}")
        else:
            print("   WARNING: No deals returned")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_flipp_api():
    """Test the Flipp API integration"""
    print("\nTesting Flipp API...")
    try:
        response = requests.post(f"{BASE_URL}/api/test-flipp")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_docker_networking():
    """Test Docker container networking"""
    print("\nTesting Docker container networking...")
    
    # Test local connectivity
    print("   Testing localhost connectivity...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   SUCCESS: Localhost connection successful")
    except:
        print(f"   ERROR: Localhost connection failed")
    
    # Test external connectivity (Google DNS)
    print("   Testing external connectivity...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print(f"   SUCCESS: External connection successful")
    except:
        print(f"   ERROR: External connection failed (DNS/network issue)")
    
    # Test Google Places API connectivity
    print("   Testing Google Places API connectivity...")
    try:
        # This will fail without proper API key but shows connectivity
        response = requests.get("https://places.googleapis.com/v1/places:searchNearby", timeout=5)
        print(f"   SUCCESS: Google API endpoint reachable (status: {response.status_code})")
    except Exception as e:
        print(f"   ERROR: Google API unreachable: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("FlyerFlutter API Test Suite")
    print("=" * 60)
    
    results = {
        "Health Check": test_health_check(),
        "API Status": test_api_status(),
        "Stores Endpoint": test_stores_endpoint(),
        "Deals Endpoint": test_deals_endpoint(),
        "Flipp API": test_flipp_api(),
    }
    
    # Network diagnostics
    test_docker_networking()
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"   {test_name}: {status}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"   Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed < total_tests:
        print("\nWARNING: Some tests failed. Check Docker logs for details:")
        print("   docker logs flyerflutter-app --tail 50")
    
    print("=" * 60)

if __name__ == "__main__":
    main()