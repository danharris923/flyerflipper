#!/usr/bin/env python3
"""
Detailed Google API test to see exact error from Railway backend.
"""

import asyncio
import httpx
import json

RAILWAY_API = "https://flyerflipper-production.up.railway.app/api"

async def test_stores_detailed():
    """Get detailed error from Railway Stores API."""
    
    print("Testing Railway Stores API with detailed error reporting...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{RAILWAY_API}/stores", params={
                "postal_code": "K1A0A6",
                "radius": 10000,
                "max_results": 5
            })
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"Error JSON: {json.dumps(error_data, indent=2)}")
                except:
                    print("Could not parse error as JSON")
            
        except Exception as e:
            print(f"Request Error: {e}")

async def test_google_directly():
    """Test Google APIs directly to compare."""
    
    print("\nTesting Google APIs directly from here...")
    print("=" * 60)
    
    # This should fail because we don't have the API key, but let's see the error
    API_KEY = "AIzaSyBHXNXC-FstJUiC92iVQWi4V5Q1WBI99m4"
    
    # Test Geocoding API
    print("1. Testing Geocoding API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("https://maps.googleapis.com/maps/api/geocode/json", params={
                "address": "K1A0A6, Canada",
                "key": API_KEY,
                "region": "CA"
            })
            print(f"   Geocoding Status: {response.status_code}")
            data = response.json()
            print(f"   Geocoding Response: {data.get('status', 'UNKNOWN')}")
            if data.get("status") != "OK":
                print(f"   Error: {data.get('error_message', 'No error message')}")
        except Exception as e:
            print(f"   Geocoding Error: {e}")
    
    # Test Places API
    print("\n2. Testing Places API...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post("https://places.googleapis.com/v1/places:searchNearby", 
                headers={
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
                    "Content-Type": "application/json"
                },
                json={
                    "includedTypes": ["grocery_store"],
                    "maxResultCount": 5,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": 45.421532,
                                "longitude": -75.697189
                            },
                            "radius": 5000.0
                        }
                    }
                }
            )
            print(f"   Places Status: {response.status_code}")
            data = response.json()
            if response.status_code != 200:
                print(f"   Places Error: {json.dumps(data, indent=2)}")
            else:
                print(f"   Places Success: Found {len(data.get('places', []))} places")
        except Exception as e:
            print(f"   Places Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stores_detailed())
    asyncio.run(test_google_directly())