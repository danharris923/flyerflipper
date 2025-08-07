"""
FlyerItem model for FlyerFlutter application.
Represents individual flyer items/deals from grocery stores.
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, func
from datetime import datetime
from typing import Optional

from ..database import Base

if False:  # TYPE_CHECKING
    from .store import Store


class FlyerItem(Base):
    """
    FlyerItem model representing a grocery deal/product from store flyers.
    
    Attributes:
        id: Primary key
        store_id: Foreign key to Store
        name: Product name
        description: Product description (optional)
        category: Product category
        price: Current price
        original_price: Original price before discount (optional)
        discount_percent: Discount percentage (optional)
        image_url: Product image URL (optional)
        flyer_url: Link to original flyer (optional)
        sale_start: Sale start date
        sale_end: Sale end date
        created_at: Record creation timestamp
        updated_at: Record update timestamp
        store: Related store
    """
    
    __tablename__ = "flyer_items"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Key
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    
    # Product Information
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    
    # Pricing Information
    price: Mapped[float] = mapped_column(Float)
    original_price: Mapped[Optional[float]] = mapped_column(Float)
    discount_percent: Mapped[Optional[float]] = mapped_column(Float)
    
    # Media and Links
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    flyer_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Sale Period
    sale_start: Mapped[datetime] = mapped_column(DateTime, index=True)
    sale_end: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # External Identifiers (for deduplication and updates)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    source: Mapped[str] = mapped_column(String(50), default="flipp")  # Source API (flipp, etc.)
    
    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="flyer_items")
    
    @property
    def savings(self) -> Optional[float]:
        """Calculate savings amount if original price is available."""
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if the deal is currently active."""
        now = datetime.utcnow()
        return self.sale_start <= now <= self.sale_end
    
    def __repr__(self) -> str:
        """String representation of FlyerItem."""
        return f"<FlyerItem(id={self.id}, name='{self.name}', price={self.price}, store_id={self.store_id})>"