"""Services package for FlyerFlutter application."""

from .google_service import GoogleService
from .flyer_service import FlippService
from .scheduler import scheduler, start_scheduler, shutdown_scheduler

# Create service instances for use across the application
google_service = GoogleService()
flipp_service = FlippService()

__all__ = [
    "GoogleService", "FlippService", 
    "google_service", "flipp_service",
    "scheduler", "start_scheduler", "shutdown_scheduler"
]