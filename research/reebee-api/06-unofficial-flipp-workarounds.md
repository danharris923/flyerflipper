# Unofficial Flipp API Workarounds (No Credentials Required)

## Overview

Based on research, there are several unofficial methods to access Flipp grocery flyer data without requiring API credentials or authentication. These methods use publicly accessible endpoints that power the Flipp mobile app and website.

## Method 1: Direct API Endpoint Access (Recommended)

### Discovered Endpoints

**Base URLs:**
```
https://backflipp.wishabi.com/flipp/
```

**Search Endpoint:**
```
https://backflipp.wishabi.com/flipp/items/search
```

**Individual Item Endpoint:**
```
https://backflipp.wishabi.com/flipp/items/{item_id}
```

### API Parameters

**Search Parameters:**
- `locale`: Language preference (e.g., "en-ca" for English-Canada)
- `postal_code`: Canadian postal code for location-based results
- `q`: Search query (merchant name and/or product)

### Example API Calls

1. **All items from Walmart:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=K1A0A6&q=Walmart
```

2. **Milk at Walmart:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=K1A0A6&q=Walmart AND milk
```

3. **Milk at all stores:**
```
https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=K1A0A6&q=milk
```

## Method 2: Python Implementation (Simple)

```python
import requests
import time

class FlippUnofficial:
    def __init__(self, rate_limit=2.0):
        self.base_url = 'https://backflipp.wishabi.com/flipp'
        self.search_url = f'{self.base_url}/items/search'
        self.item_url = f'{self.base_url}/items'
        self.rate_limit = rate_limit
        
    def search_items(self, query, postal_code, locale='en-ca'):
        """Search for items using unofficial API"""
        params = {
            'locale': locale,
            'postal_code': postal_code,
            'q': query
        }
        
        time.sleep(self.rate_limit)  # Rate limiting
        response = requests.get(self.search_url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_item_details(self, item_id):
        """Get detailed information for specific item"""
        time.sleep(self.rate_limit)  # Rate limiting
        response = requests.get(f"{self.item_url}/{item_id}")
        response.raise_for_status()
        return response.json()
    
    def search_with_details(self, query, postal_code, locale='en-ca'):
        """Search and return detailed item information"""
        search_results = self.search_items(query, postal_code, locale)
        
        items = []
        for item in search_results.get('items', []):
            item_id = item.get('flyer_item_id')
            if item_id:
                try:
                    details = self.get_item_details(item_id)
                    items.append(details)
                except Exception as e:
                    print(f"Failed to get details for item {item_id}: {e}")
                    continue
        
        return items
```

## Method 3: Selenium Web Scraping (Advanced)

For more complex scenarios, Selenium can be used to scrape Flipp data:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

def scrape_flipp_selenium(postal_code, store_name):
    # Create undetected Chrome driver
    driver = uc.Chrome()
    
    try:
        # Navigate to Flipp
        driver.get("https://flipp.com")
        
        # Set postal code (implementation depends on site structure)
        # Search for store
        # Extract flyer data
        
        # Implementation would require analyzing Flipp's current DOM structure
        
    finally:
        driver.quit()
```

## Response Data Structure

The API returns JSON data with the following structure:

```json
{
  "items": [
    {
      "flyer_item_id": "item_id",
      "name": "Product Name",
      "description": "Product Description",
      "current_price": 2.99,
      "regular_price": 3.99,
      "merchant": {
        "name": "Store Name",
        "id": "merchant_id"
      },
      "flyer": {
        "valid_from": "2024-01-01",
        "valid_to": "2024-01-07"
      },
      "image_url": "https://...",
      "category": "grocery"
    }
  ]
}
```

## Supported Canadian Stores

Based on research, the following Canadian grocery stores are available:
- Walmart Canada
- Real Canadian Superstore
- Save-On-Foods
- Freshco
- Safeway
- Food Basics
- Giant Tiger
- Fortinos
- Sobeys
- No Frills
- Metro
- Independent
- Loblaws

## Rate Limiting & Best Practices

1. **Rate Limiting**: Implement 2-3 second delays between requests
2. **Error Handling**: Handle HTTP errors gracefully
3. **Session Reuse**: Use requests.Session() for connection pooling
4. **User Agent**: Set appropriate User-Agent header
5. **Retry Logic**: Implement exponential backoff for failures

## Important Considerations

⚠️ **Legal & Ethical Considerations:**
- These are unofficial methods that could change without notice
- May violate Flipp's Terms of Service
- Use responsibly and consider contacting Flipp for official API access
- Implement appropriate rate limiting to avoid overwhelming their servers

⚠️ **Technical Limitations:**
- Endpoints may change or be removed
- Rate limiting may be implemented
- IP blocking possible with excessive usage
- Data structure may change

## Usage in Production

For production use:
1. Implement robust error handling
2. Add retry mechanisms
3. Monitor for endpoint changes
4. Consider caching responses
5. Respect rate limits
6. Have fallback data sources

## Alternative: Official Partnership

For legitimate business use, consider reaching out to Flipp/Wishabi for an official partnership or API access agreement.