"""
Pydantic schemas for Store model.
Handles validation and serialization for Store-related API operations.
"""

from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .flyer_item import FlyerItemResponse


class StoreBase(BaseModel):
    """Base schema with common Store fields."""
    
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    store_type: Optional[str] = None
    
    @field_validator('lat', 'lng')
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Validate latitude and longitude coordinates."""
        if not isinstance(v, (int, float)):
            raise ValueError('Coordinate must be a number')
        return float(v)
    
    @field_validator('lat')
    @classmethod  
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range."""
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @field_validator('lng')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range.""" 
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
    
    @field_validator('rating', mode='before')
    @classmethod
    def validate_rating(cls, v) -> Optional[float]:
        """Validate rating is within valid range."""
        if v is None:
            return None
        if not isinstance(v, (int, float)):
            raise ValueError('Rating must be a number')
        if not 0 <= v <= 5:
            raise ValueError('Rating must be between 0 and 5')
        return float(v)


class StoreCreate(StoreBase):
    """Schema for creating a new Store."""
    pass


class StoreUpdate(BaseModel):
    """Schema for updating an existing Store."""
    
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    store_type: Optional[str] = None
    
    @field_validator('rating', mode='before')
    @classmethod
    def validate_rating(cls, v) -> Optional[float]:
        """Validate rating is within valid range."""
        if v is None:
            return None
        if not 0 <= v <= 5:
            raise ValueError('Rating must be between 0 and 5')
        return float(v)


class StoreResponse(StoreBase):
    """Schema for Store responses (includes database fields)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class StoreWithItems(StoreResponse):
    """Schema for Store with related flyer items."""
    
    flyer_items: List["FlyerItemResponse"] = []


class StoreSearchResponse(StoreResponse):
    """Schema for Store search results with additional calculated fields."""
    
    distance: Optional[float] = None  # Distance from search location in km
    active_deals_count: Optional[int] = None  # Number of active deals
    
    @field_validator('distance', mode='before')
    @classmethod
    def validate_distance(cls, v) -> Optional[float]:
        """Validate distance is positive."""
        if v is None:
            return None
        if not isinstance(v, (int, float)):
            raise ValueError('Distance must be a number')
        if v < 0:
            raise ValueError('Distance must be positive')
        return float(v)


class StoreListResponse(BaseModel):
    """Schema for paginated store list responses."""
    
    stores: List[StoreSearchResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool