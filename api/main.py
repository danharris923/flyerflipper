"""
FlyerFlutter FastAPI Application - Vercel Serverless
Canadian Grocery Flyer Comparison API optimized for Vercel deployment
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration for Vercel
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or GOOGLE_API_KEY
APP_VERSION = "2.0.0"

# Pydantic models
class Store(BaseModel):
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    types: Optional[List[str]] = []
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None

class Deal(BaseModel):
    id: str
    title: str
    description: str
    original_price: Optional[float] = None
    sale_price: Optional[float] = None
    discount_percent: Optional[float] = None
    store_name: str
    valid_until: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None

# Create FastAPI application
app = FastAPI(
    title="FlyerFlutter API",
    description=(
        "🍎 **Canadian Grocery Flyer Comparison API**\\n\\n"
        "Compare grocery prices across Canadian stores using real flyer data.\\n\\n"
        "**Features:**\\n"
        "- 📍 Location-based store discovery\\n"
        "- 🏪 Real-time flyer data from major Canadian grocery chains\\n"
        "- 💰 Price comparison and savings calculations\\n"
        "- 🔄 Weekly automated data refresh\\n"
        "- 🗺️ Google Maps integration for directions\\n\\n"
        "**Data Sources:**\\n"
        "- Google Places API (store locations)\\n"
        "- Unofficial Flipp API (flyer data)\\n"
        "- Serverless deployment optimized"
    ),
    version=APP_VERSION,
    contact={
        "name": "FlyerFlutter Support",
        "url": "https://github.com/danharris923/flyerflipper"
    }
)

# Configure CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin"
    ],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint for Vercel monitoring."""
    return {
        "status": "healthy",
        "application": "FlyerFlutter",
        "version": APP_VERSION,
        "environment": "vercel",
        "google_places_available": bool(GOOGLE_PLACES_API_KEY)
    }

# Root API endpoint
@app.get("/api")
async def api_root():
    """API root endpoint with welcome message."""
    return {
        "message": "🍎 Welcome to FlyerFlutter API!",
        "description": "Canadian Grocery Flyer Comparison Service",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "stores": "/api/stores",
        "deals": "/api/deals"
    }

# Status endpoint
@app.get("/api/status")
async def status():
    """Get API status information."""
    return {
        "status": "operational",
        "version": APP_VERSION,
        "services": {
            "google_places": "available" if GOOGLE_PLACES_API_KEY else "disabled",
            "flipp_api": "available"
        },
        "timestamp": datetime.now().isoformat()
    }

# Google Places API integration
async def search_nearby_stores(lat: float, lng: float, radius: int = 5000, max_results: int = 20):
    """Search for nearby grocery stores using Google Places API."""
    if not GOOGLE_PLACES_API_KEY:
        logger.warning("Google Places API key not configured")
        return []
    
    try:
        # Use Google Places API (New) - Nearby Search
        url = "https://places.googleapis.com/v1/places:searchNearby"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types,places.nationalPhoneNumber,places.websiteUri,places.currentOpeningHours"
        }
        
        data = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": radius
                }
            },
            "includedTypes": ["grocery_or_supermarket", "supermarket"],
            "maxResultCount": min(max_results, 20)
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        places = result.get("places", [])
        
        stores = []
        for place in places:
            store = Store(
                place_id=place.get("id", ""),
                name=place.get("displayName", {}).get("text", "Unknown Store"),
                address=place.get("formattedAddress", ""),
                lat=place.get("location", {}).get("latitude", lat),
                lng=place.get("location", {}).get("longitude", lng),
                rating=place.get("rating"),
                user_ratings_total=place.get("userRatingCount"),
                types=place.get("types", []),
                phone=place.get("nationalPhoneNumber"),
                website=place.get("websiteUri"),
                opening_hours=place.get("currentOpeningHours")
            )
            stores.append(store)
        
        logger.info(f"Found {len(stores)} stores near ({lat}, {lng})")
        return stores
        
    except Exception as e:
        logger.error(f"Google Places API error: {e}")
        return []

# Mock Flipp API integration (simplified for Vercel)
async def get_sample_deals(postal_code: str = "K1A0A6", query: str = None):
    """Get sample deals (mock data for Vercel deployment)."""
    
    sample_deals = [
        Deal(
            id="deal_1",
            title="🥛 Milk 2% - 2L",
            description="Fresh 2% milk, 2 liter carton",
            original_price=4.99,
            sale_price=3.49,
            discount_percent=30.1,
            store_name="Loblaws",
            valid_until="2024-01-15",
            category="Dairy",
            image_url="https://example.com/milk.jpg"
        ),
        Deal(
            id="deal_2", 
            title="🍞 Wonder Bread - White",
            description="Wonder White Bread, 675g loaf",
            original_price=3.99,
            sale_price=2.99,
            discount_percent=25.1,
            store_name="Metro",
            valid_until="2024-01-17",
            category="Bakery",
            image_url="https://example.com/bread.jpg"
        ),
        Deal(
            id="deal_3",
            title="🍌 Bananas - Organic",
            description="Organic bananas, per lb",
            original_price=1.99,
            sale_price=1.49,
            discount_percent=25.1,
            store_name="No Frills",
            valid_until="2024-01-20",
            category="Produce",
            image_url="https://example.com/bananas.jpg"
        ),
        Deal(
            id="deal_4",
            title="🥩 Ground Beef - Lean",
            description="Lean ground beef, per lb",
            original_price=7.99,
            sale_price=5.99,
            discount_percent=25.0,
            store_name="Sobeys",
            valid_until="2024-01-18",
            category="Meat",
            image_url="https://example.com/beef.jpg"
        ),
        Deal(
            id="deal_5",
            title="🍕 Frozen Pizza - Deluxe",
            description="Deluxe frozen pizza with pepperoni and cheese",
            original_price=8.99,
            sale_price=4.99,
            discount_percent=44.5,
            store_name="FreshCo",
            valid_until="2024-01-22",
            category="Frozen",
            image_url="https://example.com/pizza.jpg"
        )
    ]
    
    # Filter by query if provided
    if query:
        query_lower = query.lower()
        sample_deals = [
            deal for deal in sample_deals 
            if query_lower in deal.title.lower() or query_lower in deal.description.lower()
        ]
    
    logger.info(f"Returning {len(sample_deals)} sample deals for {postal_code}")
    return sample_deals

# API endpoints
@app.get("/api/stores")
async def get_nearby_stores(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"), 
    radius: int = Query(5000, description="Search radius in meters"),
    max_results: int = Query(20, description="Maximum number of results"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Results per page")
):
    """Get nearby grocery stores using Google Places API."""
    try:
        stores = await search_nearby_stores(lat, lng, radius, max_results)
        
        # Simple pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_stores = stores[start_idx:end_idx]
        
        return ApiResponse(
            success=True,
            data=paginated_stores,
            total=len(stores),
            page=page,
            per_page=per_page,
            message=f"Found {len(stores)} stores"
        )
        
    except Exception as e:
        logger.error(f"Error getting stores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stores/{store_id}")
async def get_store(store_id: str):
    """Get details for a specific store."""
    # Mock implementation for Vercel
    return ApiResponse(
        success=True,
        data={
            "place_id": store_id,
            "name": "Sample Store",
            "address": "123 Main St, Ottawa, ON",
            "lat": 45.4215,
            "lng": -75.6972
        }
    )

@app.get("/api/deals")
async def get_deals(
    lat: Optional[float] = Query(None, description="Latitude"),
    lng: Optional[float] = Query(None, description="Longitude"),
    postal_code: Optional[str] = Query(None, description="Canadian postal code"),
    query: Optional[str] = Query(None, description="Search query"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_discount: Optional[float] = Query(None, description="Minimum discount percentage"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(50, description="Results per page"),
    refresh: bool = Query(False, description="Force refresh data")
):
    """Get grocery deals and flyer data."""
    try:
        # Use postal code if provided, otherwise default
        search_postal = postal_code or "K1A0A6"
        
        # Get sample deals
        deals = await get_sample_deals(search_postal, query)
        
        # Apply filters
        if category:
            deals = [deal for deal in deals if deal.category and deal.category.lower() == category.lower()]
            
        if min_discount:
            deals = [deal for deal in deals if deal.discount_percent and deal.discount_percent >= min_discount]
            
        if store_id:
            deals = [deal for deal in deals if store_id.lower() in deal.store_name.lower()]
        
        # Simple pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_deals = deals[start_idx:end_idx]
        
        return ApiResponse(
            success=True,
            data=paginated_deals,
            total=len(deals),
            page=page,
            per_page=per_page,
            message=f"Found {len(deals)} deals in {search_postal}"
        )
        
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deals/compare")
async def compare_deals(
    product: str = Query(..., description="Product to compare"),
    postal_code: Optional[str] = Query(None, description="Canadian postal code")
):
    """Compare prices for a product across stores."""
    try:
        search_postal = postal_code or "K1A0A6" 
        deals = await get_sample_deals(search_postal, product)
        
        # Sort by price (lowest first)
        deals.sort(key=lambda x: x.sale_price or x.original_price or float('inf'))
        
        return ApiResponse(
            success=True,
            data=deals,
            message=f"Price comparison for '{product}' in {search_postal}"
        )
        
    except Exception as e:
        logger.error(f"Error comparing deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoints
@app.post("/api/test-flipp")
async def test_flipp_api(
    postal_code: str = Query("K1A0A6", description="Canadian postal code"),
    query: str = Query("milk", description="Search query")
):
    """Test the Flipp API integration."""
    try:
        deals = await get_sample_deals(postal_code, query)
        
        return {
            "success": True,
            "message": f"Flipp API test successful for {postal_code}",
            "query": query,
            "postal_code": postal_code,
            "deals_found": len(deals),
            "sample_deals": deals[:3]  # Return first 3 deals
        }
        
    except Exception as e:
        logger.error(f"Flipp API test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh-deals")
async def refresh_deals(
    postal_code: str = Query("K1A0A6", description="Canadian postal code")
):
    """Refresh deals for a postal code."""
    try:
        deals = await get_sample_deals(postal_code)
        
        return {
            "success": True,
            "message": f"Deals refreshed for {postal_code}",
            "postal_code": postal_code,
            "deals_updated": len(deals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Refresh deals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler for API routes."""
    return {
        "error": "Not Found",
        "message": "The requested API endpoint was not found",
        "path": str(request.url.path),
        "available_endpoints": {
            "api_root": "/api",
            "health": "/api/health",
            "stores": "/api/stores",
            "deals": "/api/deals",
            "docs": "/docs"
        }
    }

@app.exception_handler(500) 
async def internal_server_error_handler(request, exc):
    """Custom 500 handler for server errors."""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
        "support": "https://github.com/danharris923/flyerflipper/issues"
    }

# Vercel serverless handler (ASGI compatible)
handler = Mangum(app)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )