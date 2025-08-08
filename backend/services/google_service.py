"""
Google API service integration for FlyerFlutter application.
Handles Google Places API for store discovery and Google Directions API for navigation.
"""

import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional
import time
from asyncio import Lock

from ..config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests_per_second: int):
        self.max_requests = max_requests_per_second
        self.requests = []
        self.lock = Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 second
            self.requests = [req_time for req_time in self.requests if now - req_time < 1.0]
            
            if len(self.requests) >= self.max_requests:
                # Wait until we can make another request
                sleep_time = 1.0 - (now - self.requests[0])
                await asyncio.sleep(sleep_time)
                return await self.acquire()
            
            self.requests.append(now)


class GoogleService:
    """
    Google API service for Places and Directions APIs.
    
    Handles rate limiting, error handling, and response parsing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google service.
        
        Args:
            api_key: Google API key. If None, uses settings.GOOGLE_API_KEY
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        
        if not self.api_key:
            import os
            logger.error(f"Google API key not provided! Environment variables available: GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY', 'NOT_SET')[:10] if os.getenv('GOOGLE_API_KEY') else 'NOT_SET'}")
            logger.error("Google Places functionality will be disabled. Please set GOOGLE_API_KEY environment variable.")
            self.api_key = None
            self.enabled = False
        else:
            logger.info(f"Google API service enabled with API key: {self.api_key[:8]}...")
            self.enabled = True
        
        self.places_base_url = "https://places.googleapis.com/v1"
        self.directions_base_url = "https://maps.googleapis.com/maps/api/directions"
        
        # Rate limiters for different APIs
        self.places_rate_limiter = RateLimiter(settings.GOOGLE_API_RATE_LIMIT)
        self.directions_rate_limiter = RateLimiter(settings.GOOGLE_API_RATE_LIMIT)
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(30.0)
    
    async def nearby_search(
        self, 
        lat: float, 
        lng: float, 
        radius: int = 5000,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for nearby grocery stores using Google Places API.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            radius: Search radius in meters (max 50,000)
            max_results: Maximum number of results (1-20)
            
        Returns:
            List of store dictionaries with parsed place data
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If coordinates are invalid
        """
        if not self.enabled:
            logger.error("Google Places API is disabled - no API key configured!")
            # Instead of returning fake data, try a basic search without auth
            # This will likely fail but gives a better error message
            raise ValueError("Google API key not configured. Cannot search for real stores.")
        
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        radius = min(radius, 50000)  # API maximum
        max_results = min(max(max_results, 1), 20)  # API limits
        
        url = f"{self.places_base_url}/places:searchNearby"
        
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.location,places.types,places.rating,"
                "places.nationalPhoneNumber,places.websiteUri"
            ),
            "Content-Type": "application/json"
        }
        
        body = {
            "includedTypes": ["grocery_store", "supermarket"],
            "maxResultCount": max_results,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": float(radius)
                }
            },
            "rankPreference": "DISTANCE"
        }
        
        await self.places_rate_limiter.acquire()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Making nearby search request: lat={lat}, lng={lng}, radius={radius}")
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                places = data.get("places", [])
                
                logger.info(f"Found {len(places)} nearby stores")
                return [self._parse_place(place, lat, lng) for place in places]
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Google Places API error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 429:
                    # Rate limited, wait and retry once
                    await asyncio.sleep(2)
                    return await self.nearby_search(lat, lng, radius, max_results)
                raise
            except Exception as e:
                logger.error(f"Unexpected error in nearby search: {e}")
                raise
    
    def _parse_place(self, place: Dict[str, Any], search_lat: float, search_lng: float) -> Dict[str, Any]:
        """
        Parse Google Places API response into standardized format.
        
        Args:
            place: Raw place data from API
            search_lat: Original search latitude for distance calculation
            search_lng: Original search longitude for distance calculation
            
        Returns:
            Parsed place dictionary
        """
        location = place.get("location", {})
        place_lat = location.get("latitude", 0.0)
        place_lng = location.get("longitude", 0.0)
        
        # Calculate distance from search point
        distance = self._calculate_distance(search_lat, search_lng, place_lat, place_lng)
        
        return {
            "place_id": place.get("id", ""),
            "name": place.get("displayName", {}).get("text", "Unknown Store"),
            "address": place.get("formattedAddress", ""),
            "lat": place_lat,
            "lng": place_lng,
            "phone": place.get("nationalPhoneNumber"),
            "website": place.get("websiteUri"),
            "rating": place.get("rating"),
            "store_type": self._extract_store_type(place.get("types", [])),
            "distance": distance
        }
    
    def _extract_store_type(self, types: List[str]) -> str:
        """Extract primary store type from Google Places types list."""
        priority_types = ["grocery_store", "supermarket", "food", "establishment"]
        
        for priority_type in priority_types:
            if priority_type in types:
                return priority_type
        
        return types[0] if types else "store"
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate approximate distance between two coordinates using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return round(c * r, 2)
    
    async def get_directions_url(
        self, 
        origin_lat: float, 
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving"
    ) -> str:
        """
        Generate Google Maps directions URL.
        
        Args:
            origin_lat: Starting latitude
            origin_lng: Starting longitude  
            dest_lat: Destination latitude
            dest_lng: Destination longitude
            mode: Transportation mode (driving, walking, bicycling, transit)
            
        Returns:
            Google Maps directions URL
        """
        base_url = "https://www.google.com/maps/dir/"
        origin = f"{origin_lat},{origin_lng}"
        destination = f"{dest_lat},{dest_lng}"
        
        # Google Maps URL format
        url = f"{base_url}{origin}/{destination}/@{dest_lat},{dest_lng},15z"
        
        if mode != "driving":
            mode_param = {
                "walking": "w",
                "bicycling": "b", 
                "transit": "r"
            }.get(mode, "d")  # default to driving
            url += f"/data=!3m1!4b1!4m2!4m1!3e{mode_param}"
        
        return url
    
    async def get_directions_details(
        self,
        origin_lat: float,
        origin_lng: float, 
        dest_lat: float,
        dest_lng: float,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """
        Get detailed directions from Google Directions API.
        
        Args:
            origin_lat: Starting latitude
            origin_lng: Starting longitude
            dest_lat: Destination latitude  
            dest_lng: Destination longitude
            mode: Transportation mode
            
        Returns:
            Directions details including distance, duration, and steps
        """
        url = f"{self.directions_base_url}/json"
        
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": mode,
            "key": self.api_key,
            "units": "metric"
        }
        
        await self.directions_rate_limiter.acquire()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Getting directions: {params['origin']} -> {params['destination']}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Directions API returned status: {data.get('status')}")
                    return {"error": data.get("status", "Unknown error")}
                
                routes = data.get("routes", [])
                if not routes:
                    return {"error": "No routes found"}
                
                route = routes[0]  # Use first route
                leg = route["legs"][0]  # Use first leg
                
                return {
                    "distance": leg["distance"]["text"],
                    "distance_value": leg["distance"]["value"],  # in meters
                    "duration": leg["duration"]["text"], 
                    "duration_value": leg["duration"]["value"],  # in seconds
                    "start_address": leg["start_address"],
                    "end_address": leg["end_address"],
                    "steps": len(leg.get("steps", [])),
                    "maps_url": self.get_directions_url(origin_lat, origin_lng, dest_lat, dest_lng, mode)
                }
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Directions API error: {e.response.status_code} - {e.response.text}")
                return {"error": f"API error: {e.response.status_code}"}
            except Exception as e:
                logger.error(f"Unexpected error getting directions: {e}")
                return {"error": str(e)}


# Global service instance  
google_service = GoogleService() if settings.GOOGLE_API_KEY else None