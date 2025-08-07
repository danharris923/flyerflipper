# Technical Implementation Examples

## Complete Flipp Scraper Implementation

### Full-Featured Flipp API Client
```python
import requests
import json
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FlippItem:
    """Data class for Flipp items"""
    item_id: str
    name: str
    price: Optional[float]
    original_price: Optional[float]
    discount: Optional[str]
    brand: Optional[str]
    merchant: str
    merchant_id: str
    image_url: Optional[str]
    flyer_id: Optional[str]
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    description: Optional[str]
    
    @classmethod
    def from_api_response(cls, data: Dict) -> 'FlippItem':
        """Create FlippItem from API response"""
        return cls(
            item_id=data.get('id', ''),
            name=data.get('name', ''),
            price=cls._parse_price(data.get('current_price')),
            original_price=cls._parse_price(data.get('price')),
            discount=data.get('discount', ''),
            brand=data.get('brand', ''),
            merchant=data.get('merchant', {}).get('name', ''),
            merchant_id=data.get('merchant', {}).get('id', ''),
            image_url=data.get('image_url', ''),
            flyer_id=data.get('flyer', {}).get('id', ''),
            valid_from=cls._parse_date(data.get('valid_from')),
            valid_to=cls._parse_date(data.get('valid_to')),
            description=data.get('description', '')
        )
    
    @staticmethod
    def _parse_price(price_data) -> Optional[float]:
        """Parse price from various formats"""
        if isinstance(price_data, (int, float)):
            return float(price_data)
        elif isinstance(price_data, str):
            try:
                # Remove currency symbols and convert to float
                import re
                cleaned = re.sub(r'[^\d.,]', '', price_data)
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _parse_date(date_str) -> Optional[datetime]:
        """Parse date from string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return None

class FlippAPI:
    """Complete Flipp API client with error handling and rate limiting"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        self.base_url = 'https://backflipp.wishabi.com/flipp'
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched {url} with params {params}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def search_items(self, query: str, postal_code: str, locale: str = "en-ca") -> List[FlippItem]:
        """Search for items and return structured data"""
        params = {
            'q': query,
            'postal_code': postal_code,
            'locale': locale
        }
        
        data = self._make_request('items/search', params)
        if not data:
            return []
        
        items = []
        for item_data in data.get('items', []):
            # Get detailed item information
            item_id = item_data.get('flyer_item_id')
            if item_id:
                detailed_data = self.get_item_details(item_id)
                if detailed_data:
                    items.append(FlippItem.from_api_response(detailed_data))
        
        return items
    
    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed item information"""
        return self._make_request(f'items/{item_id}')
    
    def search_by_merchant(self, merchant_name: str, postal_code: str, 
                          locale: str = "en-ca") -> List[FlippItem]:
        """Get all items from specific merchant"""
        return self.search_items(merchant_name, postal_code, locale)
    
    def search_by_product(self, product_name: str, postal_code: str,
                         locale: str = "en-ca") -> List[FlippItem]:
        """Search for specific product across all merchants"""
        return self.search_items(product_name, postal_code, locale)
    
    def compare_prices(self, product_name: str, postal_code: str,
                      locale: str = "en-ca") -> Dict[str, List[FlippItem]]:
        """Compare prices across merchants"""
        items = self.search_by_product(product_name, postal_code, locale)
        
        merchants = {}
        for item in items:
            if item.merchant not in merchants:
                merchants[item.merchant] = []
            merchants[item.merchant].append(item)
        
        return merchants

# Usage Examples
def example_usage():
    """Example usage of FlippAPI"""
    api = FlippAPI(rate_limit_delay=2.0)  # 2 second delay between requests
    postal_code = "M5V3A8"  # Toronto
    
    # Search for milk across all stores
    print("Searching for milk across all stores...")
    milk_items = api.search_by_product("milk", postal_code)
    
    for item in milk_items[:5]:  # Show first 5 results
        print(f"{item.name} at {item.merchant}: ${item.price}")
    
    # Get all Walmart deals
    print("\nGetting all Walmart deals...")
    walmart_items = api.search_by_merchant("Walmart", postal_code)
    
    for item in walmart_items[:10]:  # Show first 10 results
        print(f"{item.name}: ${item.price} (was ${item.original_price})")
    
    # Compare bread prices
    print("\nComparing bread prices...")
    bread_comparison = api.compare_prices("bread", postal_code)
    
    for merchant, items in bread_comparison.items():
        if items:
            cheapest = min(items, key=lambda x: x.price or float('inf'))
            print(f"{merchant}: {cheapest.name} - ${cheapest.price}")

if __name__ == "__main__":
    example_usage()
```

### Enhanced Selenium-Based Grocery Scraper

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class GroceryDeal:
    """Data class for grocery deals"""
    name: str
    price: Optional[float]
    original_price: Optional[float]
    discount_percent: Optional[int]
    brand: Optional[str]
    merchant: str
    image_url: Optional[str]
    description: Optional[str]
    category: Optional[str]
    valid_until: Optional[str]

class CanadianGroceryScraper:
    """Enhanced scraper for Canadian grocery stores"""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.setup_driver(headless, proxy)
        self.wait = WebDriverWait(self.driver, 20)
        self.deals: List[GroceryDeal] = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self, headless: bool, proxy: Optional[str]):
        """Setup Chrome WebDriver with options"""
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Execute script to hide webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like delays between actions"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10):
        """Safely find element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found: {by}='{value}'")
            return None
    
    def safe_click(self, element, max_retries: int = 3):
        """Safely click element with retries"""
        for attempt in range(max_retries):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(element)
                ).click()
                return True
            except Exception as e:
                self.logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    self.human_like_delay(0.5, 1.5)
        return False
    
    def handle_location_popup(self, postal_code: str):
        """Handle location selection popups"""
        try:
            # Look for common location popup patterns
            location_selectors = [
                "input[placeholder*='postal']",
                "input[placeholder*='location']", 
                "#postal-code",
                ".location-input",
                "[data-testid*='postal']"
            ]
            
            for selector in location_selectors:
                location_input = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if location_input:
                    location_input[0].clear()
                    location_input[0].send_keys(postal_code)
                    self.human_like_delay(0.5, 1.0)
                    
                    # Look for submit button
                    submit_selectors = [
                        "button[type='submit']",
                        ".location-submit",
                        "[data-testid*='submit']",
                        "button:contains('Submit')"
                    ]
                    
                    for submit_selector in submit_selectors:
                        submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, submit_selector)
                        if submit_buttons and self.safe_click(submit_buttons[0]):
                            self.human_like_delay(2, 4)
                            return True
            
        except Exception as e:
            self.logger.warning(f"Could not handle location popup: {e}")
        
        return False
    
    def scrape_loblaws_deals(self, postal_code: str) -> List[GroceryDeal]:
        """Scrape deals from Loblaws website"""
        self.logger.info("Starting Loblaws scraping...")
        
        try:
            self.driver.get('https://www.loblaws.ca/deals/all')
            self.human_like_delay(3, 5)
            
            # Handle location selection
            self.handle_location_popup(postal_code)
            
            # Wait for deals to load
            deals_container = self.safe_find_element(By.CSS_SELECTOR, '.deals-grid, .product-grid')
            if not deals_container:
                self.logger.error("Could not find deals container")
                return []
            
            # Scroll to load more deals
            self.scroll_to_load_content()
            
            # Extract deals
            deals = self._extract_loblaws_deals()
            self.logger.info(f"Found {len(deals)} deals from Loblaws")
            return deals
            
        except Exception as e:
            self.logger.error(f"Error scraping Loblaws: {e}")
            return []
    
    def scrape_metro_deals(self, postal_code: str) -> List[GroceryDeal]:
        """Scrape deals from Metro website"""
        self.logger.info("Starting Metro scraping...")
        
        try:
            self.driver.get('https://www.metro.ca/flyer')
            self.human_like_delay(3, 5)
            
            # Handle location selection
            self.handle_location_popup(postal_code)
            
            # Wait for flyer to load
            flyer_container = self.safe_find_element(By.CSS_SELECTOR, '.flyer-container, .deals-container')
            if not flyer_container:
                self.logger.error("Could not find Metro flyer container")
                return []
            
            deals = self._extract_metro_deals()
            self.logger.info(f"Found {len(deals)} deals from Metro")
            return deals
            
        except Exception as e:
            self.logger.error(f"Error scraping Metro: {e}")
            return []
    
    def scroll_to_load_content(self, max_scrolls: int = 10):
        """Scroll page to load dynamic content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.human_like_delay(2, 4)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            scrolls += 1
    
    def _extract_loblaws_deals(self) -> List[GroceryDeal]:
        """Extract deal information from Loblaws page"""
        deals = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Update selectors based on current site structure
        deal_tiles = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['deal', 'product', 'tile', 'item']
        ))
        
        for tile in deal_tiles:
            try:
                deal = GroceryDeal(
                    name=self._extract_text(tile, ['.product-name', '.deal-title', 'h3', '.title']),
                    price=self._extract_price(tile, ['.price', '.current-price', '.sale-price']),
                    original_price=self._extract_price(tile, ['.original-price', '.regular-price', '.was-price']),
                    discount_percent=self._extract_discount(tile),
                    brand=self._extract_text(tile, ['.brand', '.brand-name']),
                    merchant='Loblaws',
                    image_url=self._extract_image(tile),
                    description=self._extract_text(tile, ['.description', '.product-description']),
                    category=self._extract_text(tile, ['.category', '.department']),
                    valid_until=self._extract_text(tile, ['.valid-until', '.expires'])
                )
                
                if deal.name and deal.price:  # Only add deals with essential info
                    deals.append(deal)
                    
            except Exception as e:
                self.logger.warning(f"Error extracting deal: {e}")
                continue
        
        return deals
    
    def _extract_metro_deals(self) -> List[GroceryDeal]:
        """Extract deal information from Metro page"""
        deals = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        deal_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['flyer-item', 'deal', 'product']
        ))
        
        for element in deal_elements:
            try:
                deal = GroceryDeal(
                    name=self._extract_text(element, ['.item-name', '.product-name', 'h3']),
                    price=self._extract_price(element, ['.price', '.sale-price']),
                    original_price=self._extract_price(element, ['.regular-price', '.was-price']),
                    discount_percent=self._extract_discount(element),
                    brand=self._extract_text(element, ['.brand']),
                    merchant='Metro',
                    image_url=self._extract_image(element),
                    description=self._extract_text(element, ['.description']),
                    category=self._extract_text(element, ['.category']),
                    valid_until=None  # Metro typically shows flyer valid dates elsewhere
                )
                
                if deal.name and deal.price:
                    deals.append(deal)
                    
            except Exception as e:
                self.logger.warning(f"Error extracting Metro deal: {e}")
                continue
        
        return deals
    
    def _extract_text(self, container, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selectors"""
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                return text if text else None
        return None
    
    def _extract_price(self, container, selectors: List[str]) -> Optional[float]:
        """Extract and parse price"""
        price_text = self._extract_text(container, selectors)
        if not price_text:
            return None
        
        import re
        # Remove currency symbols and extract numbers
        numbers = re.findall(r'[\d.,]+', price_text)
        if numbers:
            try:
                return float(numbers[0].replace(',', ''))
            except ValueError:
                return None
        return None
    
    def _extract_discount(self, container) -> Optional[int]:
        """Extract discount percentage"""
        discount_text = self._extract_text(container, ['.discount', '.save', '.off'])
        if not discount_text:
            return None
        
        import re
        numbers = re.findall(r'(\d+)%', discount_text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _extract_image(self, container) -> Optional[str]:
        """Extract image URL"""
        img = container.select_one('img')
        if img:
            return img.get('src') or img.get('data-src')
        return None
    
    def save_deals_to_json(self, filename: str):
        """Save deals to JSON file"""
        deals_data = [asdict(deal) for deal in self.deals]
        with open(filename, 'w') as f:
            json.dump(deals_data, f, indent=2)
        
        self.logger.info(f"Saved {len(self.deals)} deals to {filename}")
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

# Usage example
def main():
    scraper = CanadianGroceryScraper(headless=False)  # Set to True for production
    
    try:
        postal_code = "M5V3A8"  # Toronto postal code
        
        # Scrape multiple stores
        loblaws_deals = scraper.scrape_loblaws_deals(postal_code)
        metro_deals = scraper.scrape_metro_deals(postal_code)
        
        # Combine all deals
        scraper.deals.extend(loblaws_deals)
        scraper.deals.extend(metro_deals)
        
        # Save to file
        scraper.save_deals_to_json('canadian_grocery_deals.json')
        
        # Print summary
        print(f"Total deals found: {len(scraper.deals)}")
        for deal in scraper.deals[:5]:  # Show first 5
            print(f"{deal.name} at {deal.merchant}: ${deal.price}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
```

### Data Processing and Analysis Tools

```python
import pandas as pd
import json
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class GroceryDataAnalyzer:
    """Analyze and process scraped grocery data"""
    
    def __init__(self, deals_file: str):
        self.deals_df = pd.read_json(deals_file)
        self.prepare_data()
    
    def prepare_data(self):
        """Clean and prepare data for analysis"""
        # Convert prices to numeric
        self.deals_df['price'] = pd.to_numeric(self.deals_df['price'], errors='coerce')
        self.deals_df['original_price'] = pd.to_numeric(self.deals_df['original_price'], errors='coerce')
        
        # Calculate savings
        self.deals_df['savings'] = self.deals_df['original_price'] - self.deals_df['price']
        self.deals_df['savings_percent'] = (self.deals_df['savings'] / self.deals_df['original_price'] * 100).round(2)
        
        # Clean product names
        self.deals_df['name_cleaned'] = self.deals_df['name'].str.lower().str.strip()
        
        # Add analysis timestamp
        self.deals_df['analyzed_at'] = datetime.now()
    
    def find_best_deals(self, top_n: int = 20) -> pd.DataFrame:
        """Find the best deals by savings percentage"""
        best_deals = self.deals_df[
            (self.deals_df['savings_percent'] > 0) & 
            (self.deals_df['price'] > 0)
        ].nlargest(top_n, 'savings_percent')
        
        return best_deals[['name', 'merchant', 'price', 'original_price', 'savings_percent']]
    
    def compare_stores(self) -> Dict:
        """Compare average prices across stores"""
        store_comparison = {
            'average_price': self.deals_df.groupby('merchant')['price'].mean(),
            'average_savings': self.deals_df.groupby('merchant')['savings_percent'].mean(),
            'deal_count': self.deals_df.groupby('merchant').size()
        }
        
        return store_comparison
    
    def search_product(self, product_name: str) -> pd.DataFrame:
        """Search for specific product across stores"""
        matches = self.deals_df[
            self.deals_df['name_cleaned'].str.contains(product_name.lower(), na=False)
        ].sort_values('price')
        
        return matches[['name', 'merchant', 'price', 'original_price', 'savings_percent']]
    
    def generate_price_alerts(self, target_products: List[str], max_price: float) -> List[Dict]:
        """Generate price alerts for target products under max price"""
        alerts = []
        
        for product in target_products:
            matches = self.search_product(product)
            good_deals = matches[matches['price'] <= max_price]
            
            if not good_deals.empty:
                alerts.append({
                    'product': product,
                    'deals': good_deals.to_dict('records')
                })
        
        return alerts
    
    def export_report(self, filename: str):
        """Export analysis report"""
        report = {
            'summary': {
                'total_deals': len(self.deals_df),
                'stores': self.deals_df['merchant'].unique().tolist(),
                'average_price': self.deals_df['price'].mean(),
                'average_savings': self.deals_df['savings_percent'].mean()
            },
            'best_deals': self.find_best_deals(50).to_dict('records'),
            'store_comparison': self.compare_stores(),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

# Usage example
def analyze_grocery_data():
    analyzer = GroceryDataAnalyzer('canadian_grocery_deals.json')
    
    # Find best deals
    best_deals = analyzer.find_best_deals(10)
    print("Top 10 Best Deals:")
    print(best_deals)
    
    # Search for specific products
    milk_deals = analyzer.search_product('milk')
    print(f"\nMilk deals found: {len(milk_deals)}")
    
    # Generate price alerts
    target_products = ['milk', 'bread', 'eggs', 'chicken']
    alerts = analyzer.generate_price_alerts(target_products, 5.00)
    print(f"\nPrice alerts for products under $5: {len(alerts)}")
    
    # Export report
    analyzer.export_report('grocery_analysis_report.json')

if __name__ == "__main__":
    analyze_grocery_data()
```