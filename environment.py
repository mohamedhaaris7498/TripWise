from pydantic import BaseModel
from typing import List, Optional

class NewsHeadline(BaseModel):
    title: str
    source: str
    url: Optional[str] = None
    published_at: str
    category: str
    safety_risk_level: str  # 'low', 'moderate', 'high'

class EnvironmentStatusResponse(BaseModel):
    city: str
    lat: float
    lon: float
    temperature_c: float
    humidity_percent: int
    weather_code: int
    weather_description: str
    aqi: int
    aqi_category: str
    pm2_5: float
    pm10: float
    news_headlines: List[NewsHeadline]
    safety_advisory: str
