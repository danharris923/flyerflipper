"""
Pydantic schemas for UserFilters model.
Handles validation and serialization for user preferences and filters.
"""

from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import json


class LocationPreference(BaseModel):
    """Schema for user's preferred location."""
    
    lat: float
    lng: float
    address: Optional[str] = None
    
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


class UserFiltersBase(BaseModel):
    """Base schema for user filters and preferences."""
    
    favorite_store_ids: List[int] = []
    blocked_store_ids: List[int] = []
    hidden_categories: List[str] = []
    preferred_location: Optional[LocationPreference] = None
    max_distance: float = 10.0
    enable_notifications: bool = True
    notification_categories: List[str] = []
    
    @field_validator('max_distance')
    @classmethod
    def validate_max_distance(cls, v: float) -> float:
        """Validate max distance is positive and reasonable."""
        if not isinstance(v, (int, float)):
            raise ValueError('Max distance must be a number')
        if v <= 0:
            raise ValueError('Max distance must be positive')
        if v > 1000:  # 1000km max
            raise ValueError('Max distance cannot exceed 1000km')
        return float(v)
    
    @field_validator('favorite_store_ids', 'blocked_store_ids')
    @classmethod
    def validate_store_ids(cls, v: List[int]) -> List[int]:
        """Validate store IDs are positive integers."""
        if not isinstance(v, list):
            raise ValueError('Store IDs must be a list')
        for store_id in v:
            if not isinstance(store_id, int) or store_id <= 0:
                raise ValueError('Store IDs must be positive integers')
        return list(set(v))  # Remove duplicates
    
    @field_validator('hidden_categories', 'notification_categories')
    @classmethod
    def validate_categories(cls, v: List[str]) -> List[str]:
        """Validate and normalize category names."""
        if not isinstance(v, list):
            raise ValueError('Categories must be a list')
        normalized = []
        for category in v:
            if isinstance(category, str) and category.strip():
                normalized.append(category.strip().lower())
        return list(set(normalized))  # Remove duplicates


class UserFiltersCreate(UserFiltersBase):
    """Schema for creating user filters."""
    
    session_id: Optional[str] = None
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate session ID format."""
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError('Session ID must be a non-empty string')
        return v.strip()


class UserFiltersUpdate(BaseModel):
    """Schema for updating user filters."""
    
    favorite_store_ids: Optional[List[int]] = None
    blocked_store_ids: Optional[List[int]] = None
    hidden_categories: Optional[List[str]] = None
    preferred_location: Optional[LocationPreference] = None
    max_distance: Optional[float] = None
    enable_notifications: Optional[bool] = None
    notification_categories: Optional[List[str]] = None


class UserFiltersResponse(UserFiltersBase):
    """Schema for UserFilters responses (includes database fields)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    
    @classmethod
    def from_db_model(cls, db_model) -> "UserFiltersResponse":
        """
        Convert database model to response schema.
        Handles JSON string to list/dict conversion.
        """
        data = {
            "id": db_model.id,
            "session_id": db_model.session_id,
            "max_distance": db_model.max_distance or 10.0,
            "enable_notifications": db_model.enable_notifications,
            "created_at": db_model.created_at,
            "updated_at": db_model.updated_at,
            "last_used": db_model.last_used,
        }
        
        # Parse JSON strings back to lists
        try:
            data["favorite_store_ids"] = json.loads(db_model.favorite_store_ids or "[]")
        except json.JSONDecodeError:
            data["favorite_store_ids"] = []
            
        try:
            data["blocked_store_ids"] = json.loads(db_model.blocked_store_ids or "[]")
        except json.JSONDecodeError:
            data["blocked_store_ids"] = []
            
        try:
            data["hidden_categories"] = json.loads(db_model.hidden_categories or "[]")
        except json.JSONDecodeError:
            data["hidden_categories"] = []
            
        try:
            data["notification_categories"] = json.loads(db_model.notification_categories or "[]")
        except json.JSONDecodeError:
            data["notification_categories"] = []
            
        # Parse preferred location
        try:
            if db_model.preferred_location:
                location_data = json.loads(db_model.preferred_location)
                data["preferred_location"] = LocationPreference(**location_data)
            else:
                data["preferred_location"] = None
        except (json.JSONDecodeError, TypeError):
            data["preferred_location"] = None
            
        return cls(**data)


class FiltersSummary(BaseModel):
    """Schema for filters summary/stats."""
    
    total_favorite_stores: int
    total_blocked_stores: int
    total_hidden_categories: int
    has_location_preference: bool
    last_updated: Optional[datetime] = None