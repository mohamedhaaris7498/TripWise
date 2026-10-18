from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.destination import LiveWeatherAQI

class PlanTripRequest(BaseModel):
    destination: str = Field(..., min_length=2, description="Target city or region")
    duration_days: int = Field(..., ge=1, le=30, description="Duration in days")
    start_date: Optional[str] = Field(None, description="Target start date (YYYY-MM-DD)")
    travel_priority: str = Field(
        ...,
        description="Priority profile: couple_romantic, family_kids, solo_adventure, peaceful_break, or old_age_relaxing"
    )
    max_budget: float = Field(..., ge=500.0, description="Strict total maximum budget limit in INR")
    user_age: Optional[int] = Field(None, ge=1, le=120, description="User age for age-specific pacing and amenities")

class CostBreakdown(BaseModel):
    accommodation: float
    food_dining: float
    local_transport: float
    entry_tickets: float
    miscellaneous: float
    total_estimated_cost: float
    currency: str = "INR"
    within_budget: bool = True

class AttractionItem(BaseModel):
    name: str
    special_feature: str
    estimated_cost: float
    best_time: str
    category: str

class FoodSpot(BaseModel):
    name: str
    must_try_dish: str
    cuisine_type: str
    estimated_cost: float

class StayRecommendation(BaseModel):
    name: str
    tier: str
    estimated_nightly_rate: float
    rating: float

class HighwayUtilityStop(BaseModel):
    name: str
    type: str  # 'restroom', 'petrol_pump'
    cleanliness_rating: str
    location_note: str

class TransportOption(BaseModel):
    mode: str
    estimated_cost: float
    travel_package_name: str

class DaySchedule(BaseModel):
    day_number: int
    theme: str
    attractions: List[AttractionItem]
    food_spots: List[FoodSpot]
    stays: List[StayRecommendation]
    highway_utility_stops: List[HighwayUtilityStop]
    transport_options: List[TransportOption]
    day_budget_estimate: float

class AlternativeSuggestions(BaseModel):
    suggested_dates: List[str]
    suggested_nearby_destinations: List[str]
    reasoning: str

class PlanTripResponse(BaseModel):
    trip_id: str
    destination: str
    duration_days: int
    travel_priority: str
    age_bracket: str
    max_budget: float
    cost_breakdown: CostBreakdown
    daily_itinerary: List[DaySchedule]
    travel_viability_score: int  # 0 to 100
    viability_assessment: str
    environmental_context: LiveWeatherAQI
    alternative_recommendations: Optional[AlternativeSuggestions] = None
    generated_by: str
