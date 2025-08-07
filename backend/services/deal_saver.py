"""
Service for saving flyer deals to database
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.flyer_item import FlyerItem
from ..models.store import Store
from .flyer_service import FlippService

logger = logging.getLogger(__name__)


class DealSaver:
    """Service for saving deals to database"""
    
    @staticmethod
    def get_or_create_store(db: Session, store_name: str) -> Store:
        """Get or create a store by name"""
        # Clean store name
        clean_name = store_name.strip().title()
        
        # Check if store exists
        store = db.query(Store).filter(Store.name == clean_name).first()
        if store:
            return store
        
        # Create new store
        store = Store(
            place_id=f"flipp_{store_name.lower().replace(' ', '_')}",
            name=clean_name,
            address="Online/Multiple Locations",
            lat=43.6532,  # Default Toronto coordinates
            lng=-79.3832,
            store_type="Grocery Store",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(store)
        db.commit()
        db.refresh(store)
        
        logger.info(f"Created new store: {clean_name}")
        return store
    
    @staticmethod
    def save_deals_to_db(deals: List[Dict[str, Any]], postal_code: str) -> int:
        """Save deals to database"""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for deal in deals:
                try:
                    # Get or create store
                    store_name = deal.get('merchant', 'Unknown Store')
                    store = DealSaver.get_or_create_store(db, store_name)
                    
                    # Check if deal already exists by external_id
                    external_id = deal.get('flyer_item_id', '')
                    if external_id:
                        existing = db.query(FlyerItem).filter(
                            FlyerItem.external_id == external_id
                        ).first()
                        
                        if existing:
                            # Update existing deal
                            existing.price = deal.get('current_price')
                            existing.original_price = deal.get('original_price')
                            existing.discount_percent = deal.get('discount')
                            existing.sale_end = deal.get('valid_to', datetime.utcnow() + timedelta(days=7))
                            existing.updated_at = datetime.utcnow()
                            continue
                    
                    # Create new deal
                    flyer_item = FlyerItem(
                        store_id=store.id,
                        name=deal.get('name', 'Unknown Product'),
                        description=deal.get('description', ''),
                        category=deal.get('category', 'General'),
                        price=deal.get('current_price'),
                        original_price=deal.get('original_price'),
                        discount_percent=deal.get('discount', 0),
                        image_url=deal.get('image_url', ''),
                        flyer_url=deal.get('url', ''),
                        sale_start=deal.get('valid_from', datetime.utcnow()),
                        sale_end=deal.get('valid_to', datetime.utcnow() + timedelta(days=7)),
                        external_id=external_id,
                        source='flipp',
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(flyer_item)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving deal: {e}")
                    continue
            
            # Commit all changes
            db.commit()
            logger.info(f"Saved {saved_count} deals to database")
            
            # Clean up old deals
            week_ago = datetime.utcnow() - timedelta(days=7)
            deleted = db.query(FlyerItem).filter(
                FlyerItem.sale_end < week_ago
            ).delete()
            db.commit()
            
            if deleted:
                logger.info(f"Cleaned up {deleted} expired deals")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving deals to database: {e}")
            db.rollback()
            return 0
        finally:
            db.close()


async def refresh_and_save_deals(postal_code: str) -> Dict[str, Any]:
    """Refresh deals and save to database"""
    try:
        # Get deals from Flipp API
        flipp_service = FlippService()
        result = await flipp_service.bulk_refresh_deals(postal_code)
        
        if result.get('items'):
            # Save to database
            saved = DealSaver.save_deals_to_db(result['items'], postal_code)
            
            return {
                "status": "success",
                "fetched": len(result['items']),
                "saved": saved,
                "postal_code": postal_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "no_deals",
                "fetched": 0,
                "saved": 0,
                "postal_code": postal_code,
                "error": result.get('error'),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error refreshing deals: {e}")
        return {
            "status": "error",
            "error": str(e),
            "postal_code": postal_code,
            "timestamp": datetime.utcnow().isoformat()
        }