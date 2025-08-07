# Flipp.com API Alternative Implementation

## Overview
Since Reebee doesn't provide a public API, Flipp.com offers a viable alternative with discoverable API endpoints for accessing Canadian grocery flyer data.

## API Endpoints

### Base URLs
```python
BASE_URL = 'https://flipp.com'
BACKEND_URL = 'https://backflipp.wishabi.com/flipp'
SEARCH_URL = f'{BACKEND_URL}/items/search'
ITEM_URL = f'{BACKEND_URL}/items/'
```

### Search API
**Endpoint:** `https://backflipp.wishabi.com/flipp/items/search`

**Parameters:**
- `locale`: Language preference (e.g., "en-ca" for English Canada)
- `postal_code`: Canadian postal code for location-based results
- `q`: Search query (merchant name and/or item)

### Example API Calls

1. **All items from specific merchant:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=H4A1B9&q=Walmart
```

2. **Specific item at specific merchant:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=H4A1B9&q=Walmart AND milk
```

3. **Search all merchants for item:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=H4A1B9&q=milk
```

## Python Implementation

### Basic Implementation
```python
import requests
import json

class FlippScraper:
    def __init__(self):
        self.base_url = 'https://flipp.com'
        self.backend_url = 'https://backflipp.wishabi.com/flipp'
        self.search_url = f'{self.backend_url}/items/search'
        self.item_url = f'{self.backend_url}/items/'
    
    def search_items(self, query, postal_code, locale='en-ca'):
        """Search for items using Flipp API"""
        params = {
            'locale': locale,
            'postal_code': postal_code,
            'q': query
        }
        
        response = requests.get(self.search_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_item_details(self, item_id):
        """Get detailed information for specific item"""
        url = f"{self.item_url}{item_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def search_with_details(self, query, postal_code, locale='en-ca'):
        """Search and return detailed item information"""
        search_results = self.search_items(query, postal_code, locale)
        
        items = []
        for item in search_results.get('items', []):
            item_id = item.get('flyer_item_id')
            if item_id:
                details = self.get_item_details(item_id)
                items.append(details)
        
        return items
```

### Advanced Implementation with Error Handling
```python
import requests
import time
from typing import Dict, List, Optional

class FlippAPI:
    def __init__(self, rate_limit_delay=1.0):
        self.base_url = 'https://backflipp.wishabi.com/flipp'
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
    def _make_request(self, url, params=None):
        """Make request with rate limiting and error handling"""
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def search_deals(self, postal_code: str, query: str = "", locale: str = "en-ca") -> Optional[Dict]:
        """Search for deals by postal code and query"""
        url = f"{self.base_url}/items/search"
        params = {
            'locale': locale,
            'postal_code': postal_code,
            'q': query
        }
        return self._make_request(url, params)
    
    def get_merchant_deals(self, postal_code: str, merchant: str, locale: str = "en-ca") -> Optional[Dict]:
        """Get all deals from specific merchant"""
        return self.search_deals(postal_code, merchant, locale)
    
    def search_product_across_stores(self, postal_code: str, product: str, locale: str = "en-ca") -> Optional[Dict]:
        """Search for specific product across all stores"""
        return self.search_deals(postal_code, product, locale)
```

## Supported Canadian Grocery Stores

Flipp supports major Canadian grocery chains:
- Walmart Canada
- Real Canadian Superstore  
- Save on Foods
- Freshco
- Safeway
- Food Basics
- Giant Tiger
- Fortinos
- Sobeys
- No Frills
- Metro

## Data Structure

The API returns JSON data containing:
- Item descriptions
- Prices (regular and sale)
- Images
- Merchant information
- Flyer details
- Location-based availability

## Limitations & Considerations

1. **Unofficial API** - Could change without notice
2. **Rate Limiting** - Implement delays between requests
3. **Terms of Service** - Ensure compliance with Flipp's ToS
4. **Data Accuracy** - Validate data quality and freshness
5. **Geographic Coverage** - Limited to Canadian postal codes

## Best Practices

1. **Implement proper error handling**
2. **Use session objects for connection reuse**
3. **Add rate limiting (1-2 seconds between requests)**
4. **Cache responses when appropriate**
5. **Monitor for API changes**
6. **Respect robots.txt and terms of service**