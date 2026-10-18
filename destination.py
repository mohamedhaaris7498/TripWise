from pydantic import BaseModel, Field
from typing import List, Optional

class Coordinates(BaseModel):
    lat: float
    lon: float

class DestinationItem(BaseModel):
    id: str
    name: str
    city: str
    category: str
    rating: float = Field(..., ge=1.0, le=5.0)
    estimated_cost: float
    popularity: int = Field(..., ge=1, le=100)
    coordinates: Coordinates
    description: str
    special_feature: str
    tags: List[str] = []

class DestinationListResponse(BaseModel):
    destinations: List[DestinationItem]
    total: int
    cached: bool = False

class NearbyPlace(BaseModel):
    name: str
    category: str
    distance_km: float
    rating: float
    estimated_cost: float

class LiveWeatherAQI(BaseModel):
    temperature_c: float
    humidity_percent: int
    weather_code: int
    weather_description: str
    aqi: int
    aqi_category: str
    pm2_5: float
    pm10: float

class DestinationDetailResponse(BaseModel):
    destination: DestinationItem
    nearby_options: List[NearbyPlace]
    live_environment: LiveWeatherAQI
