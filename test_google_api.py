#!/usr/bin/env python3
"""
Test script to verify Google API key functionality.
Run this after updating your .env file with the new API key.
"""

import os
import asyncio
import sys
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

async def test_google_api_key():
    """Test Google API key with multiple endpoints."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key == "YOUR_NEW_GOOGLE_API_KEY_HERE":
        print("❌ ERROR: Please set your Google API key in .env file")
        return False
    
    print(f"🔑 Testing Google API Key: {api_key[:8]}...")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Places API (New) - Nearby Search
    print("\n1️⃣ Testing Places API (New) - Nearby Search...")
    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
            "Content-Type": "application/json"
        }
        body = {
            "includedTypes": ["grocery_store"],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": 45.421532,  # Ottawa, ON
                        "longitude": -75.697189
                    },
                    "radius": 5000.0
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=body, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                places_found = len(data.get("places", []))
                print(f"   ✅ SUCCESS: Found {places_found} grocery stores near Ottawa")
                tests_passed += 1
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Geocoding API - Postal Code to Coordinates
    print("\n2️⃣ Testing Geocoding API - Postal Code...")
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": "K1A0A6, Canada",
            "key": api_key,
            "region": "CA"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK" and data["results"]:
                    location = data["results"][0]["geometry"]["location"]
                    print(f"   ✅ SUCCESS: K1A0A6 → {location['lat']}, {location['lng']}")
                    tests_passed += 1
                else:
                    print(f"   ❌ FAILED: {data['status']} - {data.get('error_message', 'Unknown error')}")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Reverse Geocoding - Coordinates to Postal Code
    print("\n3️⃣ Testing Reverse Geocoding - Coordinates to Postal Code...")
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": "45.421532,-75.697189",  # Ottawa coordinates
            "key": api_key,
            "region": "CA"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK" and data["results"]:
                    # Extract postal code
                    postal_code = None
                    for result in data["results"]:
                        for component in result.get("address_components", []):
                            if "postal_code" in component.get("types", []):
                                postal_code = component.get("short_name")
                                break
                        if postal_code:
                            break
                    
                    if postal_code:
                        print(f"   ✅ SUCCESS: Ottawa coordinates → {postal_code}")
                        tests_passed += 1
                    else:
                        print(f"   ⚠️  PARTIAL: Found location but no postal code in response")
                else:
                    print(f"   ❌ FAILED: {data['status']} - {data.get('error_message', 'Unknown error')}")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Summary
    print(f"\n📊 SUMMARY: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your Google API key is working correctly.")
        return True
    elif tests_passed > 0:
        print("⚠️  Some tests passed - check API restrictions or billing.")
        return False
    else:
        print("❌ All tests failed - check your API key and enabled services.")
        return False

def check_api_restrictions():
    """Provide guidance on API key restrictions."""
    print("\n🔧 API KEY SECURITY RECOMMENDATIONS:")
    print("1. In Google Cloud Console, restrict your API key to:")
    print("   - HTTP referrers (websites): your domain(s)")
    print("   - IP addresses: your server IPs")
    print("2. Enable only these APIs:")
    print("   - Places API (New)")
    print("   - Geocoding API")
    print("   - Maps JavaScript API (if using maps)")
    print("3. Set usage quotas to prevent abuse")
    print("4. Monitor usage in Google Cloud Console")

if __name__ == "__main__":
    print("🚀 FlyerFlutter - Google API Key Test")
    print("=" * 50)
    
    success = asyncio.run(test_google_api_key())
    check_api_restrictions()
    
    if success:
        print("\n✅ Ready to start FlyerFlutter with Docker!")
        print("   Run: docker-compose up --build")
        sys.exit(0)
    else:
        print("\n❌ Fix the API key issues before proceeding.")
        sys.exit(1)