#!/usr/bin/env python3
"""
Test the new unrestricted API key directly.
"""

import asyncio
import httpx
import json

# New unrestricted server API key
NEW_API_KEY = "AIzaSyA4PVG8XL9XfDTC55Mebt_a2fbBMKclw5s"

async def test_new_api_key():
    """Test the new unrestricted API key directly."""
    
    print("Testing New Unrestricted API Key...")
    print("=" * 50)
    print(f"Key: {NEW_API_KEY[:12]}...")
    
    # Test 1: Geocoding API
    print("\n1. Testing Geocoding API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("https://maps.googleapis.com/maps/api/geocode/json", params={
                "address": "K1A0A6, Canada",
                "key": NEW_API_KEY,
                "region": "CA"
            })
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response Status: {data.get('status', 'UNKNOWN')}")
            
            if data.get("status") == "OK":
                print("   SUCCESS: Geocoding API works!")
                if data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    print(f"   Coordinates: {location['lat']}, {location['lng']}")
            else:
                print(f"   FAILED: {data.get('error_message', 'No error message')}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Test 2: Places API (New)
    print("\n2. Testing Places API (New)...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post("https://places.googleapis.com/v1/places:searchNearby", 
                headers={
                    "X-Goog-Api-Key": NEW_API_KEY,
                    "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
                    "Content-Type": "application/json"
                },
                json={
                    "includedTypes": ["grocery_store"],
                    "maxResultCount": 3,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": 45.421532,  # Ottawa
                                "longitude": -75.697189
                            },
                            "radius": 5000.0
                        }
                    }
                }
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                places_count = len(data.get('places', []))
                print(f"   SUCCESS: Found {places_count} places!")
                if places_count > 0:
                    sample_place = data['places'][0]
                    print(f"   Sample Store: {sample_place.get('displayName', {}).get('text', 'Unknown')}")
            else:
                data = response.json()
                print(f"   FAILED: {json.dumps(data, indent=2)}")
                
        except Exception as e:
            print(f"   ERROR: {e}")

    print("\n" + "=" * 50)
    print("API Key Test Results Summary:")
    print("If both tests show SUCCESS, the new API key is working correctly!")
    print("Railway should pick up this key and the Stores API should work.")

if __name__ == "__main__":
    asyncio.run(test_new_api_key())