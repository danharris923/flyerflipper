"""
FlyerFlutter FastAPI Application - Vercel Serverless
Minimal Canadian Grocery API for Vercel deployment
"""

import json
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Simple FastAPI app
app = FastAPI(
    title="FlyerFlutter API",
    description="Canadian Grocery Price Comparison API",
    version="2.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "FlyerFlutter",
        "version": "2.0.1",
        "environment": "vercel"
    }

# API root
@app.get("/api")
def api_root():
    return {
        "message": "🍎 FlyerFlutter API",
        "version": "2.0.1",
        "endpoints": ["/api/health", "/api/deals", "/api/stores"]
    }

# Mock deals data
SAMPLE_DEALS = [
    {
        "id": 1,
        "name": "Milk 2% - 2L",
        "description": "Fresh 2% milk, 2 liter carton",
        "category": "dairy",
        "price": 3.49,
        "original_price": 4.99,
        "discount_percent": 30,
        "image_url": "https://example.com/milk.jpg",
        "store_name": "Loblaws",
        "store_id": 1,
        "sale_start": "2025-08-07T00:00:00",
        "sale_end": "2025-08-14T23:59:59",
        "created_at": "2025-08-07T00:00:00",
        "updated_at": "2025-08-07T00:00:00",
        "external_id": "deal_1",
        "source": "flipp",
        "store_distance": None,
        "rank_score": 30,
        "is_active": True,
        "days_remaining": 7
    },
    {
        "id": 2,
        "name": "Wonder Bread - White",
        "description": "Wonder White Bread, 675g loaf",
        "category": "bakery",
        "price": 2.99,
        "original_price": 3.99,
        "discount_percent": 25,
        "image_url": "https://example.com/bread.jpg",
        "store_name": "Metro",
        "store_id": 2,
        "sale_start": "2025-08-07T00:00:00",
        "sale_end": "2025-08-14T23:59:59",
        "created_at": "2025-08-07T00:00:00",
        "updated_at": "2025-08-07T00:00:00",
        "external_id": "deal_2",
        "source": "flipp",
        "store_distance": None,
        "rank_score": 25,
        "is_active": True,
        "days_remaining": 7
    },
    {
        "id": 3,
        "name": "Bananas - Organic",
        "description": "Organic bananas, per lb",
        "category": "produce",
        "price": 1.49,
        "original_price": 1.99,
        "discount_percent": 25,
        "image_url": "https://example.com/bananas.jpg",
        "store_name": "No Frills",
        "store_id": 3,
        "sale_start": "2025-08-07T00:00:00",
        "sale_end": "2025-08-14T23:59:59",
        "created_at": "2025-08-07T00:00:00",
        "updated_at": "2025-08-07T00:00:00",
        "external_id": "deal_3",
        "source": "flipp",
        "store_distance": None,
        "rank_score": 25,
        "is_active": True,
        "days_remaining": 7
    },
    {
        "id": 4,
        "name": "Ground Beef - Lean",
        "description": "Lean ground beef, per lb",
        "category": "meat",
        "price": 5.99,
        "original_price": 7.99,
        "discount_percent": 25,
        "image_url": "https://example.com/beef.jpg",
        "store_name": "Sobeys",
        "store_id": 4,
        "sale_start": "2025-08-07T00:00:00",
        "sale_end": "2025-08-14T23:59:59",
        "created_at": "2025-08-07T00:00:00",
        "updated_at": "2025-08-07T00:00:00",
        "external_id": "deal_4",
        "source": "flipp",
        "store_distance": None,
        "rank_score": 25,
        "is_active": True,
        "days_remaining": 7
    },
    {
        "id": 5,
        "name": "Frozen Pizza - Deluxe",
        "description": "Deluxe frozen pizza with pepperoni and cheese",
        "category": "frozen",
        "price": 4.99,
        "original_price": 8.99,
        "discount_percent": 44,
        "image_url": "https://example.com/pizza.jpg",
        "store_name": "FreshCo",
        "store_id": 5,
        "sale_start": "2025-08-07T00:00:00",
        "sale_end": "2025-08-14T23:59:59",
        "created_at": "2025-08-07T00:00:00",
        "updated_at": "2025-08-07T00:00:00",
        "external_id": "deal_5",
        "source": "flipp",
        "store_distance": None,
        "rank_score": 44,
        "is_active": True,
        "days_remaining": 7
    }
]

# Mock stores data
SAMPLE_STORES = [
    {
        "id": 1,
        "name": "Loblaws",
        "address": "123 Main St, Toronto, ON",
        "lat": 43.6532,
        "lng": -79.3832,
        "distance": 1.2
    },
    {
        "id": 2,
        "name": "Metro",
        "address": "456 Queen St, Toronto, ON",
        "lat": 43.6542,
        "lng": -79.3842,
        "distance": 1.5
    },
    {
        "id": 3,
        "name": "No Frills",
        "address": "789 King St, Toronto, ON",
        "lat": 43.6522,
        "lng": -79.3822,
        "distance": 0.8
    }
]

# Deals endpoint
@app.get("/api/deals")
def get_deals(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    postal_code: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    store_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    min_discount: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False)
):
    """Get deals with filtering options"""
    deals = SAMPLE_DEALS.copy()
    
    # Apply filters
    if query:
        query_lower = query.lower()
        deals = [d for d in deals if query_lower in d["name"].lower()]
    
    if category:
        deals = [d for d in deals if d["category"].lower() == category.lower()]
    
    if store_id:
        deals = [d for d in deals if d["store_id"] == store_id]
    
    if min_discount:
        deals = [d for d in deals if d["discount_percent"] >= min_discount]
    
    # Pagination
    total = len(deals)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_deals = deals[start:end]
    
    return {
        "items": paginated_deals,
        "total": total,
        "page": page,
        "per_page": per_page,
        "has_next": total > end,
        "has_prev": page > 1,
        "categories": ["dairy", "bakery", "produce", "meat", "frozen"]
    }

# Stores endpoint  
@app.get("/api/stores")
def get_stores(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: int = Query(5000),
    max_results: int = Query(20),
    page: int = Query(1),
    per_page: int = Query(20)
):
    """Get nearby stores"""
    stores = SAMPLE_STORES.copy()
    
    # Simple pagination
    total = len(stores)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_stores = stores[start:end]
    
    return {
        "stores": paginated_stores,
        "total": total,
        "page": page,
        "per_page": per_page
    }

# Test endpoint
@app.post("/api/test-flipp")
def test_flipp(
    postal_code: str = Query("K1A0A6"),
    query: str = Query("milk")
):
    """Test endpoint that returns success"""
    return {
        "success": True,
        "message": f"Test successful for {postal_code}",
        "query": query,
        "postal_code": postal_code,
        "deals_found": len(SAMPLE_DEALS)
    }

# Export for Vercel
from mangum import Mangum
handler = Mangum(app, lifespan="off")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)