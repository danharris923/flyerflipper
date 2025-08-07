"""
API routes for FlyerFlutter application.
Defines all REST API endpoints for the Canadian grocery flyer comparison app.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Store, FlyerItem
from ..schemas import (
    StoreResponse, StoreSearchResponse, StoreListResponse,
    FlyerItemSearchResponse, FlyerItemListResponse,
    DealsComparisonResponse
)
from ..services import google_service, flipp_service, scheduler

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# Store Endpoints
@router.get("/stores", response_model=StoreListResponse)
async def get_nearby_stores(
    lat: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    radius: int = Query(5000, ge=100, le=50000, description="Search radius in meters"),
    max_results: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get nearby grocery stores using Google Places API and database cache.
    
    Returns stores within the specified radius, sorted by distance.
    """
    try:
        # First, try to find stores from Google Places API
        new_stores = []
        if google_service:
            try:
                places = await google_service.nearby_search(lat, lng, radius, max_results)
                
                # Save new stores to database
                for place in places:
                    existing_store = db.execute(
                        select(Store).where(Store.place_id == place["place_id"])
                    ).scalar_one_or_none()
                    
                    if not existing_store:
                        new_store = Store(
                            place_id=place["place_id"],
                            name=place["name"],
                            address=place["address"],
                            lat=place["lat"],
                            lng=place["lng"],
                            phone=place.get("phone"),
                            website=place.get("website"),
                            rating=place.get("rating"),
                            store_type=place.get("store_type")
                        )
                        db.add(new_store)
                        new_stores.append(place)
                    else:
                        # Update existing store info
                        existing_store.rating = place.get("rating", existing_store.rating)
                        existing_store.phone = place.get("phone", existing_store.phone)
                        existing_store.website = place.get("website", existing_store.website)
                        existing_store.updated_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Added {len(new_stores)} new stores from Google Places")
                
            except Exception as e:
                logger.error(f"Error fetching from Google Places API: {e}")
        
        # Get stores from database (including newly added ones)
        stores = db.execute(select(Store)).scalars().all()
        
        # Calculate distances and filter by radius
        store_results = []
        for store in stores:
            if google_service:
                distance = google_service._calculate_distance(lat, lng, store.lat, store.lng)
            else:
                # Simple distance calculation fallback
                import math
                lat1_rad = math.radians(lat)
                lng1_rad = math.radians(lng)
                lat2_rad = math.radians(store.lat)
                lng2_rad = math.radians(store.lng)
                
                dlat = lat2_rad - lat1_rad
                dlng = lng2_rad - lng1_rad
                
                a = (math.sin(dlat / 2) ** 2 + 
                     math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
                c = 2 * math.asin(math.sqrt(a))
                distance = round(c * 6371, 2)  # Earth's radius in km
            
            if distance <= radius / 1000:  # Convert radius to km
                # Count active deals
                active_deals_count = db.execute(
                    select(func.count(FlyerItem.id)).where(
                        and_(
                            FlyerItem.store_id == store.id,
                            FlyerItem.sale_start <= datetime.utcnow(),
                            FlyerItem.sale_end >= datetime.utcnow()
                        )
                    )
                ).scalar()
                
                store_result = StoreSearchResponse(
                    **store.__dict__,
                    distance=distance,
                    active_deals_count=active_deals_count
                )
                store_results.append(store_result)
        
        # Sort by distance
        store_results.sort(key=lambda x: x.distance or float('inf'))
        
        # Pagination
        total = len(store_results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_stores = store_results[start:end]
        
        return StoreListResponse(
            stores=paginated_stores,
            total=total,
            page=page,
            per_page=per_page,
            has_next=end < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error in get_nearby_stores: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch nearby stores")


@router.get("/stores/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific store."""
    store = db.execute(select(Store).where(Store.id == store_id)).scalar_one_or_none()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return StoreResponse(**store.__dict__)


# Deal/Flyer Item Endpoints
@router.get("/deals", response_model=FlyerItemListResponse)
async def get_deals(
    lat: float = Query(None, ge=-90, le=90, description="Latitude for location-based deals"),
    lng: float = Query(None, ge=-180, le=180, description="Longitude for location-based deals"),
    postal_code: Optional[str] = Query(None, description="Canadian postal code"),
    query: Optional[str] = Query(None, description="Search query for products"),
    store_id: Optional[int] = Query(None, description="Filter by specific store"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    min_discount: Optional[float] = Query(None, ge=0, le=100, description="Minimum discount percentage"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    refresh: bool = Query(False, description="Force refresh from Flipp API"),
    db: Session = Depends(get_db)
):
    """
    Get grocery deals/flyer items with various filtering options.
    
    Can search by location, postal code, product query, store, category, or discount level.
    """
    logger.info(f"Getting deals - postal_code: {postal_code}, lat: {lat}, lng: {lng}, flipp_service: {flipp_service is not None}")
    
    try:
        # Convert coordinates to postal code if needed
        if not postal_code and lat is not None and lng is not None:
            try:
                # Use Google Geocoding to get postal code from coordinates
                import os
                google_api_key = os.getenv("GOOGLE_API_KEY")
                if google_api_key:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json"
                        params = {
                            "latlng": f"{lat},{lng}",
                            "key": google_api_key,
                            "region": "CA"  # Canada
                        }
                        response = await client.get(geocoding_url, params=params)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("results"):
                                # Extract postal code from address components
                                for result in data["results"]:
                                    for component in result.get("address_components", []):
                                        if "postal_code" in component.get("types", []):
                                            postal_code = component.get("short_name", "").replace(" ", "")
                                            logger.info(f"Converted coordinates {lat},{lng} to postal code: {postal_code}")
                                            break
                                    if postal_code:
                                        break
            except Exception as geocoding_error:
                logger.warning(f"Failed to convert coordinates to postal code: {geocoding_error}")
        
        # Always fetch real-time deals when postal code is available
        if postal_code and flipp_service:
            try:
                logger.info(f"Fetching real-time deals for postal code: {postal_code}")
                deals_response = await flipp_service.search_deals(
                    postal_code=postal_code,
                    query=query or "",
                    max_results=per_page * 2  # Get more for filtering
                )
                
                # Convert to response format and return directly
                deals = []
                for deal in deals_response.get("items", []):
                    try:
                        # Apply filters
                        if category and category.lower() not in deal.get("category", "").lower():
                            continue
                        if min_discount and deal.get("discount", 0) < min_discount:
                            continue
                            
                        # Generate unique ID from flyer_item_id or create hash
                        deal_id = deal.get("flyer_item_id", "")
                        if not deal_id or not deal_id.strip():
                            deal_id = str(hash(f"{deal.get('name', '')}{deal.get('merchant', '')}{deal.get('current_price', 0)}"))
                        
                        # Ensure price is a valid number (flyer service outputs "price", not "current_price")
                        price = deal.get("price", deal.get("current_price"))
                        if price is None:
                            price = 0.0
                        try:
                            price = float(price)
                        except (ValueError, TypeError):
                            price = 0.0
                        
                        # Handle dates (flyer service outputs "sale_start", "sale_end") 
                        now = datetime.utcnow()
                        sale_start = deal.get("sale_start", deal.get("valid_from", now))
                        sale_end = deal.get("sale_end", deal.get("valid_to", now + timedelta(days=7)))
                        
                        if not isinstance(sale_start, datetime):
                            sale_start = now
                        if not isinstance(sale_end, datetime):
                            sale_end = now + timedelta(days=7)

                        deals.append({
                            "id": abs(hash(deal_id)) % (10**9),  # Convert to positive int
                            "store_id": 1,  # Default store ID
                            "name": deal.get("name", "Unknown Product"),
                            "description": deal.get("description", ""),
                            "category": deal.get("category", "general"),
                            "price": price,
                            "original_price": deal.get("original_price"),
                            "discount_percent": deal.get("discount_percent", 0),
                            "image_url": deal.get("image_url", ""),
                            "flyer_url": deal.get("url", ""),
                            "sale_start": sale_start.isoformat() if isinstance(sale_start, datetime) else sale_start,
                            "sale_end": sale_end.isoformat() if isinstance(sale_end, datetime) else sale_end,
                            "created_at": now.isoformat(),
                            "updated_at": now.isoformat(),
                            "external_id": deal.get("external_id", ""),
                            "source": "flipp",
                            "store_name": deal.get("merchant_name", "Unknown Store"),
                            "store_distance": None,
                            "rank_score": deal.get("discount", 0)
                        })
                    except Exception as e:
                        logger.warning(f"Failed to format deal: {e}")
                        continue
                
                # Paginate results
                total = len(deals)
                paginated_deals = deals[(page-1)*per_page:page*per_page]
                
                logger.info(f"Returning {len(paginated_deals)} of {total} real-time deals")
                return FlyerItemListResponse(
                    items=paginated_deals,
                    total=total,
                    page=page,
                    per_page=per_page,
                    has_next=total > page * per_page,
                    has_prev=page > 1,
                    categories=[]
                )
                
            except Exception as refresh_error:
                logger.error(f"Error fetching real-time deals: {refresh_error}")
                # Fall back to database query below
        
        # Build query for database
        query_stmt = select(FlyerItem).join(Store)
        
        # Apply filters
        if store_id:
            query_stmt = query_stmt.where(FlyerItem.store_id == store_id)
        
        if category:
            query_stmt = query_stmt.where(FlyerItem.category.ilike(f"%{category}%"))
        
        if query:
            query_stmt = query_stmt.where(
                or_(
                    FlyerItem.name.ilike(f"%{query}%"),
                    FlyerItem.description.ilike(f"%{query}%"),
                    Store.name.ilike(f"%{query}%")
                )
            )
        
        if min_discount:
            query_stmt = query_stmt.where(FlyerItem.discount_percent >= min_discount)
        
        # Only active deals
        now = datetime.utcnow()
        query_stmt = query_stmt.where(
            and_(
                FlyerItem.sale_start <= now,
                FlyerItem.sale_end >= now
            )
        )
        
        # If location provided, add distance-based filtering (simplified)
        # In a real implementation, you'd use spatial queries
        
        # Order by best deals first (highest discount or lowest price)
        query_stmt = query_stmt.order_by(
            FlyerItem.discount_percent.desc().nulls_last(),
            FlyerItem.price.asc()
        )
        
        # Get total count
        total_stmt = select(func.count()).select_from(query_stmt.subquery())
        total = db.execute(total_stmt).scalar()
        
        # Apply pagination
        query_stmt = query_stmt.offset((page - 1) * per_page).limit(per_page)
        
        # Execute query
        flyer_items = db.execute(query_stmt).scalars().all()
        
        # Convert to response format
        items = []
        for item in flyer_items:
            store = db.execute(select(Store).where(Store.id == item.store_id)).scalar_one()
            
            item_response = FlyerItemSearchResponse(
                **item.__dict__,
                store_name=store.name,
                store_distance=None,  # Would need location calculation
                rank_score=item.discount_percent or 0.0
            )
            items.append(item_response)
        
        # Get available categories for filtering
        categories = db.execute(
            select(FlyerItem.category.distinct())
            .where(
                and_(
                    FlyerItem.sale_start <= now,
                    FlyerItem.sale_end >= now
                )
            )
        ).scalars().all()
        
        return FlyerItemListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_next=(page * per_page) < total,
            has_prev=page > 1,
            categories=[cat for cat in categories if cat]
        )
        
    except Exception as e:
        logger.error(f"Error in get_deals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch deals")


@router.get("/deals/compare")
async def compare_deals(
    product: str = Query(..., description="Product name to compare"),
    postal_code: Optional[str] = Query(None, description="Postal code for location-based comparison"),
    db: Session = Depends(get_db)
):
    """
    Compare prices for a specific product across different stores.
    
    Returns the best deal and alternative options.
    """
    try:
        # Search for the product in database
        now = datetime.utcnow()
        items = db.execute(
            select(FlyerItem)
            .join(Store)
            .where(
                and_(
                    FlyerItem.name.ilike(f"%{product}%"),
                    FlyerItem.sale_start <= now,
                    FlyerItem.sale_end >= now
                )
            )
            .order_by(FlyerItem.price.asc())
        ).scalars().all()
        
        if not items:
            # If no items in database, try to fetch from Flipp API
            if postal_code and flipp_service:
                try:
                    deals_response = await flipp_service.search_product_across_stores(
                        postal_code=postal_code,
                        product=product
                    )
                    
                    if deals_response.get("items"):
                        # Convert to comparison format
                        deal_items = deals_response["items"]
                        best_deal = deal_items[0]  # Assuming first is best
                        other_deals = deal_items[1:5]  # Up to 4 alternatives
                        
                        return {
                            "product_name": product,
                            "category": best_deal.get("category", "unknown"),
                            "best_deal": {
                                "name": best_deal.get("name"),
                                "price": best_deal.get("price"),
                                "store_name": best_deal.get("merchant_name"),
                                "savings": best_deal.get("original_price", 0) - best_deal.get("price", 0) if best_deal.get("original_price") else 0
                            },
                            "other_deals": [
                                {
                                    "name": deal.get("name"),
                                    "price": deal.get("price"),
                                    "store_name": deal.get("merchant_name")
                                }
                                for deal in other_deals
                            ],
                            "total_stores": len(deal_items),
                            "source": "flipp_api"
                        }
                except Exception as api_error:
                    logger.error(f"Error fetching from Flipp API: {api_error}")
            
            raise HTTPException(status_code=404, detail=f"No deals found for product: {product}")
        
        # Process database results
        best_item = items[0]
        best_store = db.execute(select(Store).where(Store.id == best_item.store_id)).scalar_one()
        
        other_items = items[1:5]  # Up to 4 alternatives
        
        # Calculate max savings
        prices = [item.price for item in items]
        max_savings = max(prices) - min(prices) if len(prices) > 1 else 0
        
        best_deal_response = FlyerItemSearchResponse(
            **best_item.__dict__,
            store_name=best_store.name
        )
        
        other_deals_response = []
        for item in other_items:
            store = db.execute(select(Store).where(Store.id == item.store_id)).scalar_one()
            other_deals_response.append(
                FlyerItemSearchResponse(
                    **item.__dict__,
                    store_name=store.name
                )
            )
        
        return DealsComparisonResponse(
            product_name=product,
            category=best_item.category,
            best_deal=best_deal_response,
            other_deals=other_deals_response,
            max_savings=max_savings,
            total_stores=len(set(item.store_id for item in items))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_deals: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare deals")


# API Status and Testing Endpoints
@router.get("/status")
async def api_status():
    """Get API status and service health."""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "google_places": "available" if google_service else "unavailable",
            "flipp_service": "available" if flipp_service else "unavailable",
            "scheduler": "running" if scheduler.is_running else "stopped"
        }
    }
    
    # Test Flipp API if available
    if flipp_service:
        try:
            test_result = await flipp_service.test_api_connection()
            status["services"]["flipp_api_test"] = {
                "status": test_result.get("api_status"),
                "items_found": test_result.get("items_found", 0)
            }
        except Exception as e:
            status["services"]["flipp_api_test"] = {
                "status": "error",
                "error": str(e)
            }
    
    return status


@router.post("/test-flipp")
async def test_flipp_api(
    postal_code: str = Query("K1A0A6", description="Postal code to test"),
    query: str = Query("milk", description="Product to search for")
):
    """Test the unofficial Flipp API connection."""
    if not flipp_service:
        raise HTTPException(status_code=503, detail="Flipp service not available")
    
    try:
        test_result = await flipp_service.test_api_connection(postal_code)
        
        # Also try a specific search
        search_result = await flipp_service.search_deals(postal_code, query, max_results=5)
        
        return {
            "connection_test": test_result,
            "search_test": {
                "query": query,
                "items_found": len(search_result.get("items", [])),
                "sample_item": search_result.get("items", [{}])[0] if search_result.get("items") else None
            }
        }
    except Exception as e:
        logger.error(f"Flipp API test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# Background task endpoints
@router.post("/refresh-deals")
async def trigger_deals_refresh(
    background_tasks: BackgroundTasks,
    postal_code: str = Query(..., description="Postal code to refresh deals for")
):
    """Trigger a background refresh of deals for a specific postal code."""
    
    async def refresh_task():
        """Background task to refresh deals."""
        try:
            from ..services.deal_saver import refresh_and_save_deals
            result = await refresh_and_save_deals(postal_code)
            logger.info(f"Background refresh completed: {result}")
        except Exception as e:
            logger.error(f"Background refresh failed: {e}")
    
    background_tasks.add_task(refresh_task)
    
    return {
        "message": f"Deal refresh initiated for postal code: {postal_code}",
        "status": "background_task_started"
    }