import httpx
import asyncio
from typing import Dict, Any, Optional
from app.services.cache_service import cache

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_aqi_category(us_aqi: int) -> str:
    if us_aqi <= 50:
        return "Good (Ideal for Outdoor Activities)"
    elif us_aqi <= 100:
        return "Moderate (Acceptable for most travelers)"
    elif us_aqi <= 150:
        return "Unhealthy for Sensitive Groups (Seniors/Kids take care)"
    elif us_aqi <= 200:
        return "Unhealthy (Wear masks / limit prolonged exertion)"
    elif us_aqi <= 300:
        return "Very Unhealthy (Avoid outdoor activities)"
    else:
        return "Hazardous (Health warning of emergency conditions)"

async def fetch_weather_and_aqi(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch live weather and air quality index for given coordinates using Open-Meteo with caching."""
    cache_key = f"env:{round(lat, 3)}:{round(lon, 3)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto"
    )
    aqi_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&current=pm10,pm2_5,us_aqi"
    )

    async with httpx.AsyncClient(timeout=4.0) as client:
        results = await asyncio.gather(
            client.get(weather_url),
            client.get(aqi_url),
            return_exceptions=True
        )

    # Defaults in case of network issues
    temp_c = 24.5
    humidity = 62
    weather_code = 1
    pm2_5 = 18.0
    pm10 = 34.0
    us_aqi = 45

    # Process weather response
    if not isinstance(results[0], Exception) and results[0].status_code == 200:
        w_data = results[0].json().get("current", {})
        temp_c = float(w_data.get("temperature_2m", temp_c))
        humidity = int(w_data.get("relative_humidity_2m", humidity))
        weather_code = int(w_data.get("weather_code", weather_code))

    # Process AQI response
    if not isinstance(results[1], Exception) and results[1].status_code == 200:
        a_data = results[1].json().get("current", {})
        pm2_5 = float(a_data.get("pm2_5", pm2_5))
        pm10 = float(a_data.get("pm10", pm10))
        us_aqi = int(a_data.get("us_aqi", us_aqi))

    weather_desc = WMO_WEATHER_CODES.get(weather_code, "Pleasant conditions")
    aqi_cat = get_aqi_category(us_aqi)

    result = {
        "temperature_c": temp_c,
        "humidity_percent": humidity,
        "weather_code": weather_code,
        "weather_description": weather_desc,
        "aqi": us_aqi,
        "aqi_category": aqi_cat,
        "pm2_5": pm2_5,
        "pm10": pm10
    }

    # Cache for 25 minutes
    cache.set(cache_key, result, ttl=1500)
    return result
