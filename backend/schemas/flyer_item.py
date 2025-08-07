"""
Pydantic schemas for FlyerItem model.
Handles validation and serialization for FlyerItem-related API operations.
"""

from pydantic import BaseModel, field_validator, computed_field, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .store import StoreResponse


class FlyerItemBase(BaseModel):
    """Base schema with common FlyerItem fields."""
    
    name: str
    description: Optional[str] = None
    category: str
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    flyer_url: Optional[str] = None
    sale_start: datetime
    sale_end: datetime
    external_id: Optional[str] = None
    source: str = "flipp"
    
    @field_validator('price', 'original_price')
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate price is positive."""
        if v is None:
            return None
        if not isinstance(v, (int, float)):
            raise ValueError('Price must be a number')
        if v < 0:
            raise ValueError('Price must be positive')
        return float(v)
    
    @field_validator('discount_percent')
    @classmethod
    def validate_discount_percent(cls, v: Optional[float]) -> Optional[float]:
        """Validate discount percentage is between 0 and 100."""
        if v is None:
            return None
        if not isinstance(v, (int, float)):
            raise ValueError('Discount percent must be a number')
        if not 0 <= v <= 100:
            raise ValueError('Discount percent must be between 0 and 100')
        return float(v)
    
    @field_validator('sale_end')
    @classmethod
    def validate_sale_period(cls, v: datetime, info) -> datetime:
        """Validate sale end is after sale start."""
        if 'sale_start' in info.data:
            sale_start = info.data['sale_start']
            if isinstance(sale_start, datetime) and v <= sale_start:
                raise ValueError('Sale end must be after sale start')
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is not empty and normalize."""
        if not v or not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip().lower()


class FlyerItemCreate(FlyerItemBase):
    """Schema for creating a new FlyerItem."""
    
    store_id: int
    
    @field_validator('store_id')
    @classmethod
    def validate_store_id(cls, v: int) -> int:
        """Validate store_id is positive."""
        if not isinstance(v, int) or v <= 0:
            raise ValueError('Store ID must be a positive integer')
        return v


class FlyerItemUpdate(BaseModel):
    """Schema for updating an existing FlyerItem."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    flyer_url: Optional[str] = None
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None


class FlyerItemResponse(FlyerItemBase):
    """Schema for FlyerItem responses (includes database fields)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    store_id: int
    created_at: datetime
    updated_at: datetime
    
    @computed_field
    @property
    def savings(self) -> Optional[float]:
        """Calculate savings amount if original price is available."""
        if self.original_price and self.original_price > self.price:
            return round(self.original_price - self.price, 2)
        return None
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if the deal is currently active."""
        now = datetime.utcnow()
        return self.sale_start <= now <= self.sale_end
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining until sale ends."""
        if not self.is_active:
            return 0
        delta = self.sale_end - datetime.utcnow()
        return max(0, delta.days)


class FlyerItemWithStore(FlyerItemResponse):
    """Schema for FlyerItem with related store information."""
    
    store: "StoreResponse"


class FlyerItemSearchResponse(FlyerItemResponse):
    """Schema for FlyerItem search results with additional metadata."""
    
    store_name: Optional[str] = None
    store_distance: Optional[float] = None
    rank_score: Optional[float] = None  # For ranking by savings/popularity


class FlyerItemListResponse(BaseModel):
    """Schema for paginated flyer item list responses."""
    
    items: List[FlyerItemSearchResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    categories: List[str] = []  # Available categories for filtering


class DealsComparisonResponse(BaseModel):
    """Schema for price comparison responses."""
    
    product_name: str
    category: str
    best_deal: FlyerItemSearchResponse
    other_deals: List[FlyerItemSearchResponse]
    max_savings: Optional[float] = None
    total_stores: int