from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ItineraryCreateRequest(BaseModel):
    destination_id: Optional[str] = None
    destination_name: str = Field(..., min_length=1, description="Name of destination or activity")
    category: Optional[str] = Field("attractions", description="Category of activity")
    day_number: Optional[int] = Field(1, ge=1, le=30, description="Day index in trip")
    notes: Optional[str] = Field("", description="Custom traveler notes")
    cost_estimate: Optional[float] = Field(0.0, ge=0.0, description="Estimated expense")
    details: Optional[Dict[str, Any]] = None

class ItineraryItemResponse(BaseModel):
    id: int
    user_id: int
    destination_id: Optional[str] = None
    destination_name: str
    category: str
    day_number: int
    notes: str
    cost_estimate: float
    details: Optional[Dict[str, Any]] = None
    created_at: str

class ItineraryListResponse(BaseModel):
    items: List[ItineraryItemResponse]
    total_items: int
    total_estimated_budget: float
