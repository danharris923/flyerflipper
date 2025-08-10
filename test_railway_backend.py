#!/usr/bin/env python3
"""
Test script to verify Railway backend API is working with Google services.
Run this to debug the Vercel → Railway → Google Maps connection.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Railway backend URL (from your vercel.json)
RAILWAY_BASE_URL = "https://flyerflipper-production.up.railway.app"
API_BASE_URL = f"{RAILWAY_BASE_URL}/api"

async def test_railway_backend():
    """Test Railway backend endpoints that Vercel frontend depends on."""
    
    print("Testing Railway Backend API for Vercel Google Maps Issue")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tests = []
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        try:
            response = await client.get(f"{RAILWAY_BASE_URL}/health")
            if response.status_code == 200:
                print(f"   PASS Health Check: {response.json()}")
                tests.append(("Health", True, None))
            else:
                print(f"   FAIL Health Check Failed: {response.status_code}")
                tests.append(("Health", False, f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"   FAIL Health Check Error: {e}")
            tests.append(("Health", False, str(e)))
        
        # Test 2: API Status (includes service availability)
        print("\n2. Testing API Status...")
        try:
            response = await client.get(f"{API_BASE_URL}/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   PASS API Status: {data['status']}")
                print(f"   Services:")
                for service, status in data.get('services', {}).items():
                    status_mark = "PASS" if status == "available" or status == "connected" else "FAIL"
                    print(f"      {status_mark} {service}: {status}")
                tests.append(("API Status", True, None))
            else:
                print(f"   FAIL API Status Failed: {response.status_code}")
                tests.append(("API Status", False, f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"   FAIL API Status Error: {e}")
            tests.append(("API Status", False, str(e)))
        
        # Test 3: Stores API (uses Google Geocoding + Places)
        print("\n3. Testing Stores API (Google Services)...")
        try:
            response = await client.get(f"{API_BASE_URL}/stores", params={
                "postal_code": "K1A0A6",
                "radius": 10000,
                "max_results": 5
            })
            if response.status_code == 200:
                data = response.json()
                stores_count = len(data.get('stores', []))
                print(f"   PASS Stores API: Found {stores_count} stores")
                if stores_count > 0:
                    print(f"   Sample Store: {data['stores'][0]['name']}")
                tests.append(("Stores API", True, None))
            else:
                print(f"   FAIL Stores API Failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                tests.append(("Stores API", False, f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"   FAIL Stores API Error: {e}")
            tests.append(("Stores API", False, str(e)))
        
        # Test 4: Deals API (uses Flipp service)
        print("\n4. Testing Deals API...")
        try:
            response = await client.get(f"{API_BASE_URL}/deals", params={
                "postal_code": "K1A0A6",
                "per_page": 5
            })
            if response.status_code == 200:
                data = response.json()
                deals_count = len(data.get('items', []))
                print(f"   PASS Deals API: Found {deals_count} deals")
                if deals_count > 0:
                    print(f"   Sample Deal: {data['items'][0]['name']} - ${data['items'][0]['price']}")
                tests.append(("Deals API", True, None))
            else:
                print(f"   FAIL Deals API Failed: {response.status_code}")
                tests.append(("Deals API", False, f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"   FAIL Deals API Error: {e}")
            tests.append(("Deals API", False, str(e)))
        
        # Test 5: Product Comparison API (new advanced matching)
        print("\n5. Testing Product Comparison API...")
        try:
            response = await client.get(f"{API_BASE_URL}/deals/compare", params={
                "product": "coffee",
                "postal_code": "K1A0A6"
            })
            if response.status_code == 200:
                data = response.json()
                matches = data.get('total_matches', 0)
                print(f"   PASS Comparison API: Found {matches} coffee matches")
                if data.get('best_deal'):
                    print(f"   Best Deal: {data['best_deal']['name']} - ${data['best_deal']['price']}")
                tests.append(("Comparison API", True, None))
            else:
                print(f"   FAIL Comparison API Failed: {response.status_code}")
                tests.append(("Comparison API", False, f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"   FAIL Comparison API Error: {e}")
            tests.append(("Comparison API", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in tests if success)
    total = len(tests)
    
    for test_name, success, error in tests:
        status = "PASS" if success else "FAIL"
        print(f"   {status} {test_name}")
        if error:
            print(f"      Error: {error}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! Railway backend is working correctly.")
        print("Issue is likely:")
        print("   - Google API key domain restrictions")
        print("   - CORS configuration")
        print("   - Frontend environment variables")
    elif passed == 0:
        print("\nAll tests failed! Railway backend has issues:")
        print("   - Check Railway deployment status")
        print("   - Verify environment variables are set")
        print("   - Check Railway logs for errors")
    else:
        print("\nPartial success. Check failed tests above.")
        if any("google" in str(error).lower() or "places" in str(error).lower() for _, success, error in tests if not success):
            print("Google API issues detected:")
            print("   - Verify GOOGLE_API_KEY is set in Railway")
            print("   - Check Google Cloud Console API restrictions")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_railway_backend())
    exit(0 if success else 1)