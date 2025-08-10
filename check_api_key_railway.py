#!/usr/bin/env python3
"""
Check what API key Railway is actually using and test it directly.
"""

import asyncio
import httpx

async def check_railway_api_key():
    """Check Railway's API configuration and test the key."""
    
    print("Checking Railway API Key Configuration...")
    print("=" * 50)
    
    # Test the Railway status endpoint for API key info
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("https://flyerflipper-production.up.railway.app/api/status")
            if response.status_code == 200:
                data = response.json()
                print("Railway Status Response:")
                print(f"  Services: {data.get('services', {})}")
                
                # Look for any API key indicators
                google_status = data.get('services', {}).get('google_places')
                print(f"  Google Places Status: {google_status}")
                
                if 'flipp_api_test' in data.get('services', {}):
                    flipp_test = data['services']['flipp_api_test']
                    print(f"  Flipp Test: {flipp_test}")
                
        except Exception as e:
            print(f"Error checking Railway status: {e}")

    # Test a simple stores call to see the exact error
    print("\nTesting Stores API for exact error...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://flyerflipper-production.up.railway.app/api/stores",
                params={"postal_code": "K1A0A6", "max_results": 1}
            )
            
            print(f"Stores API Response:")
            print(f"  Status: {response.status_code}")
            print(f"  Body: {response.text}")
            
            # If we get a detailed error, that helps
            if response.status_code >= 400:
                print(f"  Headers: {dict(response.headers)}")
                
        except Exception as e:
            print(f"Error testing stores API: {e}")

if __name__ == "__main__":
    asyncio.run(check_railway_api_key())