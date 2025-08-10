#!/usr/bin/env python3
"""
Test if Railway has actually updated its environment variables.
"""

import asyncio
import httpx
import time

async def test_railway_env_update():
    """Check if Railway environment has been updated."""
    
    print("Testing if Railway environment variables were updated...")
    print("=" * 60)
    
    # Check if Railway shows any signs of restart/redeploy
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get("https://flyerflipper-production.up.railway.app/api/status")
            if response.status_code == 200:
                data = response.json()
                print("Railway Status:")
                print(f"  Services: {data.get('services', {})}")
                print(f"  Timestamp: {data.get('timestamp', 'Not available')}")
                
                # Check if there are any new log entries or status changes
                services = data.get('services', {})
                google_status = services.get('google_places', 'unknown')
                print(f"  Google Places Status: {google_status}")
                
                # If Railway was updated, it might show different behavior
                flipp_test = services.get('flipp_api_test', {})
                if isinstance(flipp_test, dict):
                    print(f"  Flipp Test Items: {flipp_test.get('items_found', 'N/A')}")
                
        except Exception as e:
            print(f"Error checking Railway status: {e}")
    
    print("\nTesting minimal Stores API call...")
    # Try a minimal stores call with verbose error reporting
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "https://flyerflipper-production.up.railway.app/api/stores",
                params={
                    "postal_code": "K1A0A6", 
                    "max_results": 1,
                    "radius": 5000
                }
            )
            
            print(f"Stores API Test:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Content-Length: {response.headers.get('content-length', 'N/A')}")
            print(f"  Response Body: {response.text}")
            
            # Look for any changes in error messages
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    detail = error_data.get('detail', 'No detail')
                    print(f"  Error Detail: {detail}")
                    
                    # If the error is different, Railway might have updated
                    if detail != "Failed to fetch nearby stores":
                        print("  *** Different error - Railway may have updated! ***")
                except:
                    print("  Could not parse error as JSON")
                    
        except Exception as e:
            print(f"Error testing stores API: {e}")
    
    print("\nRailway Environment Update Status:")
    print("- If you see the same 'Failed to fetch nearby stores' error,")
    print("  Railway may not have picked up the new API key yet")
    print("- Railway environment updates can take 1-2 minutes to propagate")
    print("- You may need to restart the Railway service manually")

if __name__ == "__main__":
    asyncio.run(test_railway_env_update())