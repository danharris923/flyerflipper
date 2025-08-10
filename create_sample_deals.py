#!/usr/bin/env python3
"""
Create 100 sample deals for testing the FlyerFlutter application.
Generates realistic grocery deals across various categories and stores.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import get_db, init_db
from backend.models import Store, FlyerItem
from backend.config import settings
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for realistic deals
SAMPLE_STORES = [
    {"name": "Walmart Supercentre", "address": "100 Bayshore Dr, Ottawa, ON K2B 8C1", "lat": 45.3536, "lng": -75.7981, "place_id": "ChIJ_walmart_ottawa"},
    {"name": "Loblaws", "address": "363 Richmond Rd, Ottawa, ON K2A 0E7", "lat": 45.3842, "lng": -75.7542, "place_id": "ChIJ_loblaws_ottawa"},
    {"name": "Metro", "address": "1980 Scott St, Ottawa, ON K1Z 8L8", "lat": 45.3678, "lng": -75.7234, "place_id": "ChIJ_metro_ottawa"},
    {"name": "Sobeys", "address": "1500 Merivale Rd, Nepean, ON K2E 6Z5", "lat": 45.3456, "lng": -75.7456, "place_id": "ChIJ_sobeys_ottawa"},
    {"name": "No Frills", "address": "2210 Bank St, Ottawa, ON K1V 1J5", "lat": 45.3234, "lng": -75.6789, "place_id": "ChIJ_nofrills_ottawa"},
    {"name": "FreshCo", "address": "1910 Bank St, Ottawa, ON K1V 7Z6", "lat": 45.3567, "lng": -75.6890, "place_id": "ChIJ_freshco_ottawa"},
    {"name": "Giant Tiger", "address": "2387 Ogilvie Rd, Gloucester, ON K1J 7N4", "lat": 45.4123, "lng": -75.6234, "place_id": "ChIJ_gianttiger_ottawa"},
    {"name": "Real Canadian Superstore", "address": "3045 Carling Ave, Ottawa, ON K2B 7K2", "lat": 45.3789, "lng": -75.7890, "place_id": "ChIJ_superstore_ottawa"},
]

SAMPLE_PRODUCTS = [
    # Coffee products
    {"name": "SToK Cold Brew Coffee Black", "category": "beverages", "price_range": (5.99, 8.49), "brands": ["SToK"]},
    {"name": "Starbucks Pike Place Coffee", "category": "beverages", "price_range": (8.99, 12.49), "brands": ["Starbucks"]},
    {"name": "Tim Hortons Original Blend Coffee", "category": "beverages", "price_range": (7.99, 10.99), "brands": ["Tim Hortons"]},
    {"name": "Folgers Classic Roast Coffee", "category": "beverages", "price_range": (6.49, 9.99), "brands": ["Folgers"]},
    {"name": "Maxwell House Original Coffee", "category": "beverages", "price_range": (5.99, 8.99), "brands": ["Maxwell House"]},
    {"name": "STOK Cold Brew Coffee Vanilla", "category": "beverages", "price_range": (6.49, 8.99), "brands": ["SToK"]},
    
    # Milk products
    {"name": "Neilson Milk 2%", "category": "dairy", "price_range": (4.99, 6.49), "brands": ["Neilson"]},
    {"name": "Beatrice Milk 1%", "category": "dairy", "price_range": (4.89, 6.29), "brands": ["Beatrice"]},
    {"name": "Natrel Organic Milk", "category": "dairy", "price_range": (5.99, 7.49), "brands": ["Natrel"]},
    {"name": "Lactantia Milk Whole", "category": "dairy", "price_range": (5.49, 6.99), "brands": ["Lactantia"]},
    {"name": "Dairyland Milk Skim", "category": "dairy", "price_range": (4.79, 6.19), "brands": ["Dairyland"]},
    
    # Bread products
    {"name": "Wonder Bread White", "category": "bakery", "price_range": (2.99, 4.49), "brands": ["Wonder"]},
    {"name": "Dempsters Whole Wheat Bread", "category": "bakery", "price_range": (3.49, 4.99), "brands": ["Dempsters"]},
    {"name": "Country Harvest Multigrain", "category": "bakery", "price_range": (3.99, 5.49), "brands": ["Country Harvest"]},
    {"name": "McGavin's Sourdough Bread", "category": "bakery", "price_range": (4.49, 5.99), "brands": ["McGavin's"]},
    
    # Cheese products
    {"name": "Black Diamond Cheddar Cheese", "category": "dairy", "price_range": (5.99, 8.49), "brands": ["Black Diamond"]},
    {"name": "Saputo Mozzarella Cheese", "category": "dairy", "price_range": (6.49, 8.99), "brands": ["Saputo"]},
    {"name": "Armstrong Cheese Marble", "category": "dairy", "price_range": (6.99, 9.49), "brands": ["Armstrong"]},
    
    # Meat products
    {"name": "Maple Leaf Bacon", "category": "meat", "price_range": (5.99, 8.99), "brands": ["Maple Leaf"]},
    {"name": "Schneiders Deli Ham", "category": "meat", "price_range": (7.49, 10.99), "brands": ["Schneiders"]},
    {"name": "Fresh Ground Beef 80/20", "category": "meat", "price_range": (8.99, 12.99), "brands": ["Fresh"]},
    {"name": "PC Chicken Breasts", "category": "meat", "price_range": (9.99, 14.99), "brands": ["PC"]},
    
    # Produce
    {"name": "Organic Bananas", "category": "produce", "price_range": (2.49, 3.99), "brands": ["Organic"]},
    {"name": "Red Delicious Apples", "category": "produce", "price_range": (3.99, 5.49), "brands": ["Fresh"]},
    {"name": "Yellow Onions 3lb Bag", "category": "produce", "price_range": (2.99, 4.49), "brands": ["Fresh"]},
    {"name": "Baby Carrots 2lb", "category": "produce", "price_range": (3.49, 4.99), "brands": ["Fresh"]},
    
    # Snacks
    {"name": "Lays Potato Chips Original", "category": "snacks", "price_range": (3.99, 5.49), "brands": ["Lays"]},
    {"name": "Doritos Nacho Cheese", "category": "snacks", "price_range": (4.49, 6.99), "brands": ["Doritos"]},
    {"name": "Oreo Original Cookies", "category": "snacks", "price_range": (4.99, 6.99), "brands": ["Oreo"]},
    {"name": "Pringles Original", "category": "snacks", "price_range": (2.99, 4.99), "brands": ["Pringles"]},
    
    # Beverages
    {"name": "Coca Cola 12 Pack", "category": "beverages", "price_range": (5.99, 8.99), "brands": ["Coca Cola"]},
    {"name": "Pepsi 24 Pack", "category": "beverages", "price_range": (8.99, 12.99), "brands": ["Pepsi"]},
    {"name": "Tropicana Orange Juice", "category": "beverages", "price_range": (4.99, 6.99), "brands": ["Tropicana"]},
    {"name": "Simply Lemonade", "category": "beverages", "price_range": (3.99, 5.49), "brands": ["Simply"]},
    
    # Frozen foods
    {"name": "McCain French Fries", "category": "frozen", "price_range": (3.99, 5.99), "brands": ["McCain"]},
    {"name": "Haagen Dazs Ice Cream", "category": "frozen", "price_range": (6.99, 9.99), "brands": ["Haagen Dazs"]},
    {"name": "Birds Eye Vegetables", "category": "frozen", "price_range": (2.99, 4.49), "brands": ["Birds Eye"]},
    
    # Pantry staples
    {"name": "Barilla Pasta Spaghetti", "category": "pantry", "price_range": (1.99, 3.49), "brands": ["Barilla"]},
    {"name": "Campbell's Tomato Soup", "category": "pantry", "price_range": (1.49, 2.99), "brands": ["Campbell's"]},
    {"name": "Quaker Oats Large", "category": "pantry", "price_range": (4.99, 6.99), "brands": ["Quaker"]},
    {"name": "Minute Rice White", "category": "pantry", "price_range": (3.99, 5.99), "brands": ["Minute"]},
    
    # Cereals
    {"name": "Cheerios Original", "category": "pantry", "price_range": (5.99, 8.49), "brands": ["Cheerios"]},
    {"name": "Frosted Flakes", "category": "pantry", "price_range": (5.49, 7.99), "brands": ["Kellogg's"]},
    {"name": "Lucky Charms", "category": "pantry", "price_range": (5.99, 8.99), "brands": ["General Mills"]},
    
    # Household items
    {"name": "Tide Laundry Detergent", "category": "household", "price_range": (12.99, 18.99), "brands": ["Tide"]},
    {"name": "Charmin Toilet Paper 12 Pack", "category": "household", "price_range": (14.99, 19.99), "brands": ["Charmin"]},
    {"name": "Dawn Dish Soap", "category": "household", "price_range": (3.99, 5.99), "brands": ["Dawn"]},
]

def create_sample_stores(db: Session):
    """Create sample stores if they don't exist."""
    existing_stores = db.query(Store).count()
    if existing_stores > 0:
        logger.info(f"Found {existing_stores} existing stores, skipping store creation")
        return db.query(Store).all()
    
    logger.info("Creating sample stores...")
    stores = []
    for store_data in SAMPLE_STORES:
        store = Store(
            name=store_data["name"],
            address=store_data["address"],
            lat=store_data["lat"],
            lng=store_data["lng"],
            place_id=store_data["place_id"],
            rating=round(random.uniform(3.8, 4.8), 1),
            store_type="grocery"
        )
        db.add(store)
        stores.append(store)
    
    db.commit()
    logger.info(f"Created {len(stores)} stores")
    return stores

def generate_deal_variations(base_product, store, deal_number):
    """Generate variations of a product for different deals."""
    variations = [
        base_product["name"],
        f"{base_product['name']} - Family Size",
        f"{base_product['name']} 2 Pack",
        f"{base_product['name']} Mega Pack",
        f"Sale - {base_product['name']}",
        f"{base_product['name']} Special Offer"
    ]
    
    # Pick a variation based on deal number for some consistency
    variation_index = deal_number % len(variations)
    return variations[variation_index]

def create_sample_deals(db: Session, stores, num_deals=100):
    """Create sample deals."""
    logger.info(f"Creating {num_deals} sample deals...")
    
    # Clear existing deals
    db.query(FlyerItem).delete()
    db.commit()
    
    now = datetime.utcnow()
    deals_created = 0
    
    for i in range(num_deals):
        # Pick random product and store
        product = random.choice(SAMPLE_PRODUCTS)
        store = random.choice(stores)
        
        # Generate price within range
        min_price, max_price = product["price_range"]
        current_price = round(random.uniform(min_price, max_price), 2)
        
        # Sometimes add original price for discount calculation
        original_price = None
        discount_percent = None
        if random.random() < 0.4:  # 40% chance of having a discount
            discount_amount = random.uniform(0.50, 3.00)
            original_price = round(current_price + discount_amount, 2)
            discount_percent = round((discount_amount / original_price) * 100, 1)
        
        # Generate product name variation
        product_name = generate_deal_variations(product, store, i)
        
        # Generate sale dates (current deals)
        sale_start = now - timedelta(days=random.randint(0, 3))
        sale_end = now + timedelta(days=random.randint(3, 10))
        
        # Create the deal
        deal = FlyerItem(
            store_id=store.id,
            name=product_name,
            description=f"Great deal on {product['name']} at {store.name}",
            category=product["category"],
            price=current_price,
            original_price=original_price,
            discount_percent=discount_percent,
            image_url=f"https://example.com/images/{product['name'].lower().replace(' ', '_')}.jpg",
            flyer_url=f"https://flipp.com/store/{store.name.lower().replace(' ', '_')}",
            sale_start=sale_start,
            sale_end=sale_end,
            external_id=f"deal_{i:03d}_{store.id}",
            source="sample_data"
        )
        
        db.add(deal)
        deals_created += 1
        
        if deals_created % 20 == 0:
            logger.info(f"Created {deals_created}/{num_deals} deals...")
    
    db.commit()
    logger.info(f"Successfully created {deals_created} sample deals")
    
    # Print summary by category
    category_counts = {}
    for deal in db.query(FlyerItem).all():
        category_counts[deal.category] = category_counts.get(deal.category, 0) + 1
    
    logger.info("Deals by category:")
    for category, count in sorted(category_counts.items()):
        logger.info(f"  {category}: {count} deals")

def main():
    """Main function to create sample data."""
    try:
        logger.info("🚀 Creating 100 sample deals for FlyerFlutter")
        
        # Initialize database
        init_db()
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create stores
            stores = create_sample_stores(db)
            
            # Create deals
            create_sample_deals(db, stores, num_deals=100)
            
            logger.info("✅ Successfully created all sample data!")
            logger.info("🛍️ You can now test the improved comparison logic with real data")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()