"""Services package for FlyerFlutter application."""

from .google_service import GoogleService
from .flyer_service import FlippService
from .scheduler import scheduler, start_scheduler, shutdown_scheduler
from .product_matcher import ProductMatcher

# Create service instances for use across the application
google_service = GoogleService()
flipp_service = FlippService()
product_matcher = ProductMatcher()

__all__ = [
    "GoogleService", "FlippService", "ProductMatcher",
    "google_service", "flipp_service", "product_matcher",
    "scheduler", "start_scheduler", "shutdown_scheduler"
]