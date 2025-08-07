# Canadian Grocery Store Web Scraping Implementation

## Overview
Comprehensive guide for web scraping Canadian grocery stores using Python, including major chains like Loblaws, Metro, Sobeys, and Walmart Canada.

## Key Canadian Grocery Chains

### Major Players
- **Loblaws Group**: Loblaws, Real Canadian Superstore, No Frills, Zehrs, Valumart, Wholesale Club
- **Metro Inc.**: Metro, Food Basics
- **Sobeys**: Sobeys, Safeway, Freshco, IGA
- **Walmart Canada**
- **Save-On-Foods**

## Technical Approaches

### 1. Selenium-Based Scraping (Recommended)

Most Canadian grocery store websites use JavaScript for dynamic content loading, making Selenium essential.

#### grocery-helpers Library
```python
# Selenium-based Python API for Canadian grocery retailers
# Supports: Real Canadian Superstore, Loblaws, Zehrs, Valumart, 
# Wholesale Club, Metro, Walmart Grocery, Instacart, and others

from grocery_helpers import RealCanadianSuperstoreScraper

scraper = RealCanadianSuperstoreScraper()
deals = scraper.get_deals()
```

#### Custom Selenium Implementation
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class CanadianGroceryScraper:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
    
    def scrape_loblaws_deals(self, postal_code):
        """Scrape deals from Loblaws website"""
        try:
            self.driver.get('https://www.loblaws.ca/deals/all')
            
            # Handle location selection
            self._handle_location_selection(postal_code)
            
            # Wait for deals to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'deal-tile'))
            )
            
            # Extract deal information
            deals = self._extract_deals()
            return deals
            
        except Exception as e:
            print(f"Error scraping Loblaws: {e}")
            return []
    
    def _handle_location_selection(self, postal_code):
        """Handle location/postal code selection popup"""
        try:
            location_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'postal-code-input'))
            )
            location_input.clear()
            location_input.send_keys(postal_code)
            
            submit_btn = self.driver.find_element(By.ID, 'location-submit')
            submit_btn.click()
            
            time.sleep(3)  # Wait for page to update
            
        except Exception as e:
            print(f"Could not set location: {e}")
    
    def _extract_deals(self):
        """Extract deal information from loaded page"""
        deals = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        deal_tiles = soup.find_all('div', class_='deal-tile')
        
        for tile in deal_tiles:
            deal = {
                'name': self._safe_extract(tile, '.product-name'),
                'price': self._safe_extract(tile, '.price'),
                'original_price': self._safe_extract(tile, '.original-price'),
                'discount': self._safe_extract(tile, '.discount'),
                'image_url': self._safe_extract_attr(tile, '.product-image img', 'src'),
                'brand': self._safe_extract(tile, '.brand-name')
            }
            deals.append(deal)
        
        return deals
    
    def _safe_extract(self, container, selector):
        """Safely extract text from element"""
        element = container.select_one(selector)
        return element.get_text(strip=True) if element else None
    
    def _safe_extract_attr(self, container, selector, attr):
        """Safely extract attribute from element"""
        element = container.select_one(selector)
        return element.get(attr) if element else None
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
```

### 2. API Reverse Engineering

#### Loblaws Store Locator API
```python
import requests

def get_loblaws_stores(postal_code):
    """Get Loblaws stores by postal code using their API"""
    url = "https://www.loblaws.ca/api/stores/search"
    params = {
        'location': postal_code,
        'radius': 25,  # km
        'limit': 10
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.loblaws.ca/'
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def get_store_flyers(store_id):
    """Get flyers for specific Loblaws store"""
    url = f"https://www.loblaws.ca/api/flyers/{store_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    return response.json()
```

### 3. Network Traffic Inspection

Many developers have found success by:
1. Using browser developer tools to inspect network traffic
2. Finding XHR/Fetch requests that load product data
3. Replicating these API calls in Python

```python
# Example of discovered API endpoint structure
def inspect_network_traffic():
    """
    Common findings from network inspection:
    
    1. Product data often loaded via XHR requests
    2. JSON responses with product arrays
    3. Location-based filtering via postal codes
    4. Pagination parameters for large datasets
    """
    
    # Typical API structure found:
    api_patterns = {
        'products': '/api/products/search',
        'deals': '/api/deals/current', 
        'flyers': '/api/flyers/active',
        'stores': '/api/stores/nearby'
    }
    
    return api_patterns
```

## Implementation Challenges

### 1. Dynamic Content Loading
- Most Canadian grocery sites use React/Vue.js
- Content loads after initial page load
- Requires waiting for JavaScript execution

### 2. Location-Based Content
- Different deals based on postal code
- Location selection popups
- Store-specific inventory

### 3. Anti-Bot Measures
- CAPTCHAs on some sites
- Rate limiting
- IP-based blocking
- User-agent detection

### 4. Data Structure Variations
- Different HTML structures across chains
- Frequent website updates
- Inconsistent product data formats

## Best Practices

### 1. Ethical Scraping
```python
import time
import random

class EthicalScraper:
    def __init__(self, min_delay=2, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
    
    def polite_delay(self):
        """Random delay between requests"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def respect_robots_txt(self, url):
        """Check robots.txt before scraping"""
        # Implementation to check robots.txt
        pass
```

### 2. Error Handling and Retry Logic
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RobustScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def safe_request(self, url, **kwargs):
        """Make request with error handling"""
        try:
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
```

### 3. Data Validation and Cleaning
```python
import re
from typing import Optional

class DataCleaner:
    @staticmethod
    def clean_price(price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extra whitespace
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        
        try:
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                # Assume comma is thousands separator
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Assume comma is decimal separator (European style)
                cleaned = cleaned.replace(',', '.')
            
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def normalize_product_name(name: str) -> str:
        """Standardize product names"""
        if not name:
            return ""
        
        # Remove extra whitespace and convert to title case
        return " ".join(name.strip().split()).title()
```

## Store-Specific Implementation Notes

### Loblaws Group
- Location selection required
- React-based interface
- API endpoints discoverable
- Strong anti-bot measures

### Metro
- Simpler HTML structure
- Less JavaScript-dependent
- Regional pricing variations
- Store locator API available

### Sobeys
- Heavy JavaScript usage
- Complex product categorization
- Regional banner variations (Safeway, IGA, etc.)

### Walmart Canada
- Similar to US site structure
- Good API documentation (unofficial)
- Product availability by postal code
- Rollback deals prominently featured

## Legal and Compliance Considerations

1. **Respect robots.txt files**
2. **Follow website terms of service**
3. **Implement reasonable rate limiting**
4. **Don't overload servers**
5. **Consider PIPEDA compliance for Canadian data**
6. **Be transparent about data usage**

## Recommended Libraries

```python
# Core scraping libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import requests

# Data handling
import pandas as pd
import json

# Async scraping (for better performance)
import aiohttp
import asyncio

# Image processing (for flyer OCR)
from PIL import Image
import pytesseract
```