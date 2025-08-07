"""
Store model for FlyerFlutter application.
Represents grocery stores retrieved from Google Places API.
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, func
from datetime import datetime
from typing import Optional, List

from ..database import Base

if False:  # TYPE_CHECKING  
    from .flyer_item import FlyerItem


class Store(Base):
    """
    Store model representing a grocery store.
    
    Attributes:
        id: Primary key
        place_id: Google Places API unique identifier
        name: Store name
        address: Store address
        lat: Latitude coordinate
        lng: Longitude coordinate
        phone: Store phone number (optional)
        website: Store website (optional)
        rating: Google Places rating (optional)
        store_type: Type of store (grocery_store, supermarket, etc.)
        created_at: Record creation timestamp
        updated_at: Record update timestamp
        flyer_items: Related flyer items
    """
    
    __tablename__ = "stores"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Google Places API fields
    place_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    address: Mapped[str] = mapped_column(String(500))
    lat: Mapped[float] = mapped_column(Float, index=True)
    lng: Mapped[float] = mapped_column(Float, index=True)
    
    # Optional fields
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    rating: Mapped[Optional[float]] = mapped_column(Float)
    store_type: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    flyer_items: Mapped[List["FlyerItem"]] = relationship(
        "FlyerItem", 
        back_populates="store",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of Store."""
        return f"<Store(id={self.id}, name='{self.name}', place_id='{self.place_id}')>"