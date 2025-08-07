"""
UserFilters model for FlyerFlutter application.
Represents user preferences and filters (stored without user identification).
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, func
from datetime import datetime
from typing import Optional

from ..database import Base


class UserFilters(Base):
    """
    UserFilters model representing user preferences and filters.
    
    Note: This is a simplified model that doesn't require user authentication.
    Instead, it can be used to store session-based or anonymous user preferences.
    
    Attributes:
        id: Primary key
        session_id: Anonymous session identifier (optional)
        favorite_store_ids: JSON string of favorite store IDs
        blocked_store_ids: JSON string of blocked store IDs  
        hidden_categories: JSON string of hidden product categories
        preferred_location: JSON string of user's preferred location
        max_distance: Maximum distance for store search in km
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "user_filters"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Session Identification (for anonymous users)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, unique=True)
    
    # Filter Preferences (stored as JSON strings)
    favorite_store_ids: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["1", "2", "3"]
    blocked_store_ids: Mapped[Optional[str]] = mapped_column(Text)   # JSON array: ["4", "5"] 
    hidden_categories: Mapped[Optional[str]] = mapped_column(Text)   # JSON array: ["bakery", "deli"]
    
    # Location Preferences
    preferred_location: Mapped[Optional[str]] = mapped_column(Text)  # JSON: {"lat": 45.5, "lng": -73.6, "address": "Montreal, QC"}
    max_distance: Mapped[Optional[float]] = mapped_column(default=10.0)  # km
    
    # Notification Preferences
    enable_notifications: Mapped[bool] = mapped_column(default=True)
    notification_categories: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    def __repr__(self) -> str:
        """String representation of UserFilters."""
        return f"<UserFilters(id={self.id}, session_id='{self.session_id}')>"
        
    @classmethod
    def create_for_session(cls, session_id: str) -> "UserFilters":
        """
        Factory method to create default filters for a new session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            UserFilters: New instance with default values
        """
        return cls(
            session_id=session_id,
            favorite_store_ids="[]",
            blocked_store_ids="[]", 
            hidden_categories="[]",
            max_distance=10.0,
            enable_notifications=True,
            last_used=datetime.utcnow()
        )