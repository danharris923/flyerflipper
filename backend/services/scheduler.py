"""
Scheduler service for FlyerFlutter application.
Handles weekly flyer refresh and other background tasks using APScheduler.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..config import settings
from ..database import SessionLocal
from ..models import Store, FlyerItem
from .flyer_service import flipp_service
from .google_service import google_service

logger = logging.getLogger(__name__)


class FlyerFlutterScheduler:
    """
    Background task scheduler for FlyerFlutter application.
    
    Handles:
    - Weekly flyer refresh
    - Store data updates
    - Data cleanup tasks
    """
    
    def __init__(self):
        """Initialize the scheduler with configuration."""
        self.scheduler = None
        self.is_running = False
        
        # Job store and executor configuration
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 30
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='America/Toronto'  # Eastern timezone for Canadian market
        )
    
    def start(self):
        """Start the scheduler with all configured jobs."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule weekly flyer refresh
            self.scheduler.add_job(
                self.refresh_all_flyers,
                CronTrigger(
                    day_of_week='thu',  # Thursday is typically when new flyers are released
                    hour=settings.FLYER_UPDATE_HOUR,  # Default: 6 AM
                    minute=0
                ),
                id='weekly_flyer_refresh',
                name='Weekly Flyer Refresh',
                replace_existing=True
            )
            
            # Schedule daily cleanup
            self.scheduler.add_job(
                self.cleanup_expired_deals,
                CronTrigger(
                    hour=2,  # 2 AM daily
                    minute=0
                ),
                id='daily_cleanup',
                name='Daily Cleanup of Expired Deals',
                replace_existing=True
            )
            
            # Schedule store data refresh (weekly on Sunday)
            self.scheduler.add_job(
                self.refresh_store_data,
                CronTrigger(
                    day_of_week='sun',
                    hour=3,  # 3 AM Sunday
                    minute=0
                ),
                id='weekly_store_refresh',
                name='Weekly Store Data Refresh',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started with all jobs configured")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")
    
    async def refresh_all_flyers(self):
        """
        Refresh flyer data for all stores in the database.
        This is the main scheduled job that runs weekly.
        """
        logger.info("Starting weekly flyer refresh")
        
        db = SessionLocal()
        try:
            # Get all unique postal codes from stores
            stores = db.execute(select(Store)).scalars().all()
            postal_codes = set()
            
            for store in stores:
                # Extract postal code from address (simplified approach)
                postal_code = self._extract_postal_code_from_address(store.address)
                if postal_code:
                    postal_codes.add(postal_code)
            
            logger.info(f"Found {len(postal_codes)} unique postal codes for refresh")
            
            total_new_items = 0
            total_updated_items = 0
            errors = []
            
            for postal_code in postal_codes:
                try:
                    result = await self._refresh_flyers_for_postal_code(db, postal_code)
                    total_new_items += result.get('new_items', 0)
                    total_updated_items += result.get('updated_items', 0)
                    
                    # Rate limiting between postal codes
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    error_msg = f"Failed to refresh flyers for {postal_code}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            logger.info(
                f"Flyer refresh completed: {total_new_items} new items, "
                f"{total_updated_items} updated items, {len(errors)} errors"
            )
            
        except Exception as e:
            logger.error(f"Critical error in flyer refresh: {e}")
        finally:
            db.close()
    
    async def _refresh_flyers_for_postal_code(
        self, 
        db: Session, 
        postal_code: str
    ) -> dict:
        """
        Refresh flyers for a specific postal code.
        
        Args:
            db: Database session
            postal_code: Canadian postal code
            
        Returns:
            Dictionary with refresh statistics
        """
        try:
            # Get all deals for this postal code
            deals_response = await flipp_service.bulk_refresh_deals(postal_code)
            deals = deals_response.get('items', [])
            
            new_items = 0
            updated_items = 0
            
            for deal in deals:
                try:
                    # Find matching store by merchant name
                    store = self._find_store_by_merchant(db, deal.get('merchant_name', ''))
                    if not store:
                        continue
                    
                    # Check if item already exists
                    external_id = deal.get('external_id')
                    if not external_id:
                        continue
                    
                    existing_item = db.execute(
                        select(FlyerItem).where(
                            FlyerItem.external_id == external_id,
                            FlyerItem.store_id == store.id
                        )
                    ).scalar_one_or_none()
                    
                    if existing_item:
                        # Update existing item
                        self._update_flyer_item(existing_item, deal)
                        updated_items += 1
                    else:
                        # Create new item
                        new_item = self._create_flyer_item(deal, store.id)
                        db.add(new_item)
                        new_items += 1
                        
                except Exception as e:
                    logger.error(f"Error processing deal: {e}")
                    continue
            
            db.commit()
            logger.info(f"Postal code {postal_code}: {new_items} new, {updated_items} updated")
            
            return {
                'new_items': new_items,
                'updated_items': updated_items,
                'postal_code': postal_code
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error refreshing flyers for {postal_code}: {e}")
            return {'new_items': 0, 'updated_items': 0, 'postal_code': postal_code}
    
    def _find_store_by_merchant(self, db: Session, merchant_name: str) -> Optional[Store]:
        """Find store in database by merchant name."""
        if not merchant_name:
            return None
            
        # Normalize merchant name for matching
        normalized_name = merchant_name.lower().strip()
        
        stores = db.execute(select(Store)).scalars().all()
        
        for store in stores:
            if normalized_name in store.name.lower():
                return store
        
        return None
    
    def _create_flyer_item(self, deal: dict, store_id: int) -> FlyerItem:
        """Create new FlyerItem from deal data."""
        return FlyerItem(
            store_id=store_id,
            name=deal.get('name', ''),
            description=deal.get('description'),
            category=deal.get('category', 'other'),
            price=deal.get('price', 0.0),
            original_price=deal.get('original_price'),
            discount_percent=deal.get('discount_percent'),
            image_url=deal.get('image_url'),
            flyer_url=deal.get('flyer_url'),
            sale_start=deal.get('sale_start', datetime.utcnow()),
            sale_end=deal.get('sale_end', datetime.utcnow() + timedelta(days=7)),
            external_id=deal.get('external_id'),
            source=deal.get('source', 'flipp')
        )
    
    def _update_flyer_item(self, item: FlyerItem, deal: dict):
        """Update existing FlyerItem with new deal data."""
        item.name = deal.get('name', item.name)
        item.description = deal.get('description', item.description)
        item.category = deal.get('category', item.category)
        item.price = deal.get('price', item.price)
        item.original_price = deal.get('original_price', item.original_price)
        item.discount_percent = deal.get('discount_percent', item.discount_percent)
        item.image_url = deal.get('image_url', item.image_url)
        item.flyer_url = deal.get('flyer_url', item.flyer_url)
        item.sale_start = deal.get('sale_start', item.sale_start)
        item.sale_end = deal.get('sale_end', item.sale_end)
        item.updated_at = datetime.utcnow()
    
    def _extract_postal_code_from_address(self, address: str) -> Optional[str]:
        """Extract Canadian postal code from address string."""
        import re
        
        if not address:
            return None
        
        # Look for Canadian postal code pattern
        match = re.search(r'[A-Z]\d[A-Z]\s?\d[A-Z]\d', address.upper())
        if match:
            return match.group().replace(' ', '')
        
        return None
    
    async def cleanup_expired_deals(self):
        """Remove expired flyer items from database."""
        logger.info("Starting cleanup of expired deals")
        
        db = SessionLocal()
        try:
            # Delete items that expired more than 7 days ago
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            expired_items = db.execute(
                select(FlyerItem).where(FlyerItem.sale_end < cutoff_date)
            ).scalars().all()
            
            count = len(expired_items)
            
            for item in expired_items:
                db.delete(item)
            
            db.commit()
            logger.info(f"Cleaned up {count} expired deals")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during cleanup: {e}")
        finally:
            db.close()
    
    async def refresh_store_data(self):
        """Refresh store information from Google Places API."""
        logger.info("Starting weekly store data refresh")
        
        if not google_service:
            logger.warning("Google service not available, skipping store refresh")
            return
        
        db = SessionLocal()
        try:
            stores = db.execute(select(Store)).scalars().all()
            updated_count = 0
            
            for store in stores:
                try:
                    # Perform a simple nearby search to get updated info
                    places = await google_service.nearby_search(
                        store.lat, store.lng, radius=100, max_results=1
                    )
                    
                    if places:
                        place = places[0]
                        # Update store with fresh data
                        store.rating = place.get('rating', store.rating)
                        store.phone = place.get('phone', store.phone)
                        store.website = place.get('website', store.website)
                        store.updated_at = datetime.utcnow()
                        updated_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error refreshing store {store.id}: {e}")
                    continue
            
            db.commit()
            logger.info(f"Refreshed {updated_count} stores")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during store refresh: {e}")
        finally:
            db.close()


# Global scheduler instance
scheduler = FlyerFlutterScheduler()


def start_scheduler():
    """Start the global scheduler."""
    scheduler.start()


def shutdown_scheduler():
    """Shutdown the global scheduler.""" 
    scheduler.shutdown()