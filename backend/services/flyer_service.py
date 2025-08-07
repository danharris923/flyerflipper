"""
Flipp API service integration for FlyerFlutter application.
Handles fetching grocery flyer data from Flipp's unofficial API endpoints.

IMPORTANT: This uses unofficial/undocumented API endpoints discovered through research.
These endpoints do not require credentials but may change without notice.
Use responsibly and consider rate limiting.
"""

import asyncio
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
from asyncio import Lock
import hashlib
import re


logger = logging.getLogger(__name__)


class FlippRateLimiter:
    """Rate limiter specifically tuned for Flipp API."""
    
    def __init__(self, max_requests_per_second: int = 2):
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
                sleep_time = 1.0 - (now - self.requests[0]) + 0.5  # Extra buffer
                await asyncio.sleep(sleep_time)
                return await self.acquire()
            
            self.requests.append(now)


class FlippService:
    """
    Flipp API service for fetching Canadian grocery flyer data.
    
    Uses Flipp's unofficial but accessible API endpoints to retrieve
    grocery deals and pricing information across Canadian stores.
    
    IMPORTANT: This service uses unofficial endpoints discovered through research:
    - https://backflipp.wishabi.com/flipp/items/search (search items)
    - https://backflipp.wishabi.com/flipp/items/{id} (item details)
    
    No credentials required, but endpoints may change without notice.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Flipp service with unofficial API endpoints.
        
        Args:
            base_url: Flipp API base URL. If None, uses discovered endpoint
        """
        # Use discovered unofficial endpoint if no base URL provided
        self.base_url = base_url or "https://backflipp.wishabi.com/flipp"
        self.search_url = f"{self.base_url}/items/search"
        self.item_url = f"{self.base_url}/items"
        
        # Conservative rate limiting for unofficial API
        self.rate_limiter = FlippRateLimiter(max_requests_per_second=2)
        
        # HTTP client configuration with realistic headers
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-CA,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://flipp.com/",
            "Origin": "https://flipp.com"
        }
        
        # Supported Canadian grocery stores (confirmed working)
        self.supported_merchants = [
            "walmart", "superstore", "real canadian superstore", "save-on-foods", 
            "freshco", "safeway", "food basics", "giant tiger", "fortinos", 
            "sobeys", "no frills", "metro", "loblaws", "independent",
            "your independent grocer", "valu-mart", "zehrs"
        ]
        
        logger.info(f"FlippService initialized with unofficial endpoint: {self.base_url}")
        logger.warning("Using unofficial Flipp API endpoints - may change without notice")
    
    def _normalize_postal_code(self, postal_code: str) -> str:
        """
        Normalize Canadian postal code format.
        
        Args:
            postal_code: Raw postal code input
            
        Returns:
            Normalized postal code in format A1B2C3
            
        Raises:
            ValueError: If postal code format is invalid
        """
        # Remove spaces and convert to uppercase
        normalized = re.sub(r'\s+', '', postal_code.upper())
        
        # Validate Canadian postal code format
        if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', normalized):
            raise ValueError("Invalid Canadian postal code format")
        
        return normalized
    
    def _generate_external_id(self, item_data: Dict[str, Any]) -> str:
        """
        Generate a unique external ID for an item to prevent duplicates.
        
        Args:
            item_data: Raw item data from Flipp API
            
        Returns:
            Unique external ID string
        """
        # Create hash from merchant, item name, price, and sale dates
        key_data = f"{item_data.get('merchant', '')}-{item_data.get('name', '')}-{item_data.get('price', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    async def get_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific flyer item.
        
        Args:
            item_id: Flipp item ID from search results
            
        Returns:
            Detailed item information or None if not found
        """
        if not item_id:
            return None
            
        await self.rate_limiter.acquire()
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                logger.debug(f"Fetching item details for ID: {item_id}")
                response = await client.get(f"{self.item_url}/{item_id}")
                response.raise_for_status()
                
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"Failed to get item details for {item_id}: {e.response.status_code}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error getting item details: {e}")
                return None

    async def search_deals(
        self,
        postal_code: str,
        query: str = "",
        locale: str = "en-ca",
        max_results: int = 100,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Search for deals using unofficial Flipp API endpoint.
        
        Args:
            postal_code: Canadian postal code
            query: Search query (product or merchant name)
            locale: Language locale (default: en-ca)
            max_results: Maximum number of results to return
            include_details: Whether to fetch detailed item information
            
        Returns:
            Parsed API response with deals
            
        Raises:
            ValueError: If postal code is invalid
            httpx.HTTPError: If API request fails
        """
        normalized_postal = self._normalize_postal_code(postal_code)
        
        params = {
            "locale": locale,
            "postal_code": normalized_postal,
            "q": query.strip()
        }
        
        await self.rate_limiter.acquire()
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            try:
                logger.info(f"Searching deals: postal={normalized_postal}, query='{query}' (unofficial API)")
                response = await client.get(self.search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                logger.info(f"Raw API returned {len(items)} items")
                
                # Limit results
                limited_items = items[:max_results]
                parsed_items = []
                
                # Process each item - optionally fetch details
                for item in limited_items:
                    try:
                        if include_details:
                            # Get detailed information for better data
                            item_id = item.get('flyer_item_id')
                            if item_id:
                                detailed_item = await self.get_item_details(str(item_id))
                                if detailed_item:
                                    item.update(detailed_item)
                        
                        parsed_item = self._parse_flyer_item(item)
                        if parsed_item:
                            parsed_items.append(parsed_item)
                    except Exception as e:
                        logger.warning(f"Failed to process item: {e}")
                        continue
                
                logger.info(f"Successfully parsed {len(parsed_items)} valid deals")
                return {
                    "items": parsed_items,
                    "total": len(parsed_items),
                    "postal_code": normalized_postal,
                    "query": query,
                    "api_response_count": len(items),
                    "include_details": include_details,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Flipp API error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 429:
                    # Rate limited, wait longer and retry once
                    await asyncio.sleep(5)
                    return await self.search_deals(postal_code, query, locale, max_results)
                elif e.response.status_code in [400, 404]:
                    # Client error - return empty results
                    return {"items": [], "total": 0, "error": f"API error {e.response.status_code}"}
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Flipp search: {e}")
                raise
    
    async def get_merchant_deals(
        self,
        postal_code: str,
        merchant: str,
        locale: str = "en-ca"
    ) -> Dict[str, Any]:
        """
        Get all deals from a specific merchant.
        
        Args:
            postal_code: Canadian postal code
            merchant: Merchant name (e.g., "walmart", "metro")
            locale: Language locale
            
        Returns:
            Deals from specified merchant
        """
        # Normalize merchant name
        merchant_normalized = merchant.lower().replace(" ", "-")
        
        if merchant_normalized not in self.supported_merchants:
            logger.warning(f"Merchant '{merchant}' may not be supported")
        
        return await self.search_deals(postal_code, merchant, locale)
    
    async def search_product_across_stores(
        self,
        postal_code: str,
        product: str,
        locale: str = "en-ca"
    ) -> Dict[str, Any]:
        """
        Search for a specific product across all stores.
        
        Args:
            postal_code: Canadian postal code  
            product: Product name to search for
            locale: Language locale
            
        Returns:
            Product deals across multiple stores
        """
        return await self.search_deals(postal_code, product, locale)
    
    def _parse_flyer_item(self, raw_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse raw Flipp API item into standardized format.
        
        Args:
            raw_item: Raw item data from Flipp API
            
        Returns:
            Parsed item dictionary or None if invalid
        """
        try:
            # Extract basic information
            name = raw_item.get("name", "").strip()
            if not name:
                return None
                
            # Price information
            current_price = raw_item.get("current_price")
            regular_price = raw_item.get("regular_price") 
            
            if current_price is None:
                return None  # Price is required
            
            # Merchant information - handle both direct string and nested dict
            merchant_name = (
                raw_item.get("merchant_name") or  # Direct string (like "Costco")
                (raw_item.get("merchant", {}).get("name") if isinstance(raw_item.get("merchant"), dict) else None) or  # Nested dict
                str(raw_item.get("merchant", "Unknown Store"))  # Fallback
            )
            
            # Flyer information
            flyer = raw_item.get("flyer", {})
            if isinstance(flyer, dict):
                sale_start_str = flyer.get("valid_from")
                sale_end_str = flyer.get("valid_to")
            else:
                sale_start_str = None
                sale_end_str = None
            
            # Parse dates
            sale_start = self._parse_date(sale_start_str) or datetime.utcnow()
            sale_end = self._parse_date(sale_end_str) or (datetime.utcnow() + timedelta(days=7))
            
            # Calculate discount
            discount_percent = None
            if regular_price and regular_price > current_price:
                discount_percent = round(((regular_price - current_price) / regular_price) * 100, 1)
            
            # Category (try to extract from description or name)
            category = self._extract_category(name, raw_item.get("description", ""))
            
            return {
                "name": name,
                "description": raw_item.get("description"),
                "category": category,
                "price": float(current_price),
                "original_price": float(regular_price) if regular_price else None,
                "discount_percent": discount_percent,
                "image_url": raw_item.get("clean_image_url") or raw_item.get("clipping_image_url") or raw_item.get("image_url"),
                "flyer_url": raw_item.get("flyer_url"),
                "sale_start": sale_start,
                "sale_end": sale_end,
                "external_id": self._generate_external_id(raw_item),
                "source": "flipp",
                "merchant_name": merchant_name,
                "raw_data": raw_item  # For debugging and future enhancements
            }
            
        except Exception as e:
            logger.error(f"Error parsing flyer item: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from Flipp API."""
        if not date_str:
            return None
            
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"]:
                try:
                    return datetime.strptime(date_str.replace("Z", ""), fmt.replace(".%fZ", ""))
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _extract_category(self, name: str, description: str = "") -> str:
        """
        Extract product category from name and description.
        
        Args:
            name: Product name
            description: Product description
            
        Returns:
            Inferred category
        """
        text = f"{name} {description}".lower()
        
        # Category mapping based on common grocery terms
        category_keywords = {
            "produce": ["apple", "banana", "orange", "potato", "onion", "carrot", "fruit", "vegetable"],
            "meat": ["chicken", "beef", "pork", "turkey", "ham", "bacon", "sausage", "meat"],
            "dairy": ["milk", "cheese", "yogurt", "butter", "cream", "dairy"],
            "bakery": ["bread", "cake", "cookie", "bakery", "bagel", "muffin"],
            "frozen": ["frozen", "ice cream", "pizza"],
            "pantry": ["pasta", "rice", "sauce", "soup", "cereal", "canned"],
            "beverages": ["juice", "soda", "water", "coffee", "tea", "drink"],
            "snacks": ["chips", "cracker", "candy", "chocolate", "snack"],
            "health": ["vitamin", "medicine", "pharmacy", "health"],
            "household": ["cleaner", "detergent", "paper", "household"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "other"
    
    async def test_api_connection(self, postal_code: str = "K1A0A6") -> Dict[str, Any]:
        """
        Test the unofficial Flipp API connection with a simple search.
        
        Args:
            postal_code: Test postal code (default: Ottawa, Canada)
            
        Returns:
            Test results and API status
        """
        logger.info(f"Testing unofficial Flipp API connection with postal code: {postal_code}")
        
        try:
            # Test basic search
            test_result = await self.search_deals(postal_code, "milk", max_results=5)
            
            # Test item details if items are found
            details_test = None
            if test_result.get("items"):
                first_item = test_result["items"][0]
                external_id = first_item.get("external_id")
                if external_id:
                    # Try to get more details (though external_id != flyer_item_id)
                    details_test = {"status": "external_id_found", "id": external_id}
            
            return {
                "api_status": "working",
                "endpoint": self.search_url,
                "test_query": "milk",
                "postal_code": postal_code,
                "items_found": len(test_result.get("items", [])),
                "raw_response_count": test_result.get("api_response_count", 0),
                "details_test": details_test,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"API test failed: {e}")
            return {
                "api_status": "failed",
                "endpoint": self.search_url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def bulk_refresh_deals(self, postal_code: str) -> Dict[str, Any]:
        """
        Refresh deals for all supported merchants at once.
        
        Args:
            postal_code: Canadian postal code
            
        Returns:
            Aggregated deals from all merchants
        """
        logger.info(f"Starting bulk refresh for postal code: {postal_code}")
        all_deals = []
        errors = []
        successful_merchants = []
        
        # First test the API
        api_test = await self.test_api_connection(postal_code)
        if api_test.get("api_status") != "working":
            logger.error(f"API test failed before bulk refresh: {api_test.get('error')}")
            return {
                "items": [],
                "total": 0,
                "error": "API connection test failed",
                "test_result": api_test
            }
        
        # Process merchants in smaller batches
        batch_size = 3
        for i in range(0, len(self.supported_merchants), batch_size):
            batch = self.supported_merchants[i:i + batch_size]
            logger.info(f"Processing merchant batch {i//batch_size + 1}: {batch}")
            
            for merchant in batch:
                try:
                    merchant_deals = await self.get_merchant_deals(postal_code, merchant)
                    if merchant_deals.get("items"):
                        all_deals.extend(merchant_deals["items"])
                        successful_merchants.append(merchant)
                        logger.info(f"✓ Retrieved {len(merchant_deals['items'])} deals from {merchant}")
                    else:
                        logger.info(f"⚠ No deals found for {merchant}")
                    
                    # Rate limiting between merchants
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    error_msg = f"Failed to get deals from {merchant}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Longer delay between batches
            await asyncio.sleep(5)
        
        logger.info(f"Bulk refresh completed: {len(all_deals)} total deals from {len(successful_merchants)} merchants")
        
        return {
            "items": all_deals,
            "total": len(all_deals),
            "merchants_processed": len(self.supported_merchants),
            "successful_merchants": successful_merchants,
            "failed_merchants": len(errors),
            "errors": errors,
            "postal_code": postal_code,
            "api_test": api_test,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global service instance
flipp_service = FlippService()