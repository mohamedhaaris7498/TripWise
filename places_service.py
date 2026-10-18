import asyncio
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.cache_service import cache
from app.services.weather_service import fetch_weather_and_aqi

# Comprehensive destination & utility dataset
CURATED_DESTINATIONS: List[Dict[str, Any]] = [
    # CHENNAI & TAMIL NADU
    {
        "id": "dest_chn_01",
        "name": "Marina Beach Promenade & Lighthouse",
        "city": "Chennai",
        "category": "attractions",
        "rating": 4.6,
        "estimated_cost": 50.0,
        "popularity": 96,
        "coordinates": {"lat": 13.0499, "lon": 80.2824},
        "description": "The second longest natural urban beach in the world, renowned for crisp sea breezes, vibrant evening street food, and historic colonial monuments.",
        "special_feature": "Panoramic 360-degree Bay of Bengal view from the historic functioning lighthouse elevator.",
        "tags": ["beach", "kid_friendly", "attractions", "romantic", "senior_friendly"]
    },
    {
        "id": "dest_chn_02",
        "name": "Kapaleeshwarar Ancient Temple",
        "city": "Chennai",
        "category": "attractions",
        "rating": 4.8,
        "estimated_cost": 20.0,
        "popularity": 92,
        "coordinates": {"lat": 13.0336, "lon": 80.2699},
        "description": "7th-century Dravidian temple adorned with a towering gopuram, intricate stucco sculptures, and sacred temple tank.",
        "special_feature": "Living Shaivite temple rituals, traditional carnatic music reverberations, and flat accessible courtyards.",
        "tags": ["heritage", "senior_friendly", "peaceful_break", "attractions"]
    },
    {
        "id": "dest_chn_03",
        "name": "Murugan Idli Shop & Filter Coffee",
        "city": "Chennai",
        "category": "food",
        "rating": 4.7,
        "estimated_cost": 220.0,
        "popularity": 94,
        "coordinates": {"lat": 13.0418, "lon": 80.2337},
        "description": "Legendary South Indian vegetarian dining spot celebrated for piping hot ghee podi idlis, medu vadas, and authentic chicory-blended filter coffee.",
        "special_feature": "Four distinct fresh chutneys served steaming on clean plantain leaves.",
        "tags": ["food", "kid_friendly", "senior_friendly"]
    },
    {
        "id": "dest_chn_04",
        "name": "The Leela Palace Sea-Facing Stays",
        "city": "Chennai",
        "category": "accommodation",
        "rating": 4.9,
        "estimated_cost": 12500.0,
        "popularity": 89,
        "coordinates": {"lat": 13.0163, "lon": 80.2778},
        "description": "Ultra-luxurious Chettinad palace-inspired oceanfront hotel offering infinity pools, world-class spas, and panoramic sea vistas.",
        "special_feature": "Private balconies directly overlooking the azure estuary of Adyar river and Bay of Bengal.",
        "tags": ["accommodation", "romantic", "luxury"]
    },
    {
        "id": "dest_chn_05",
        "name": "Highway Oasis Clean Restroom & Cafe (OMR / ECR Toll)",
        "city": "Chennai",
        "category": "restrooms",
        "rating": 4.5,
        "estimated_cost": 10.0,
        "popularity": 80,
        "coordinates": {"lat": 12.8710, "lon": 80.2260},
        "description": "Spotlessly sanitized 24/7 rest stop featuring touchless washbasins, accessible disability-friendly toilets, baby diaper changing rooms, and tea station.",
        "special_feature": "Certified hourly ISO sanitized restroom facility with zero waiting lines.",
        "tags": ["restrooms", "senior_friendly", "highway_stop"]
    },
    {
        "id": "dest_chn_06",
        "name": "Indian Oil / BPCL 24/7 Mega Highway Fuel & EV Station",
        "city": "Chennai",
        "category": "petrol_pumps",
        "rating": 4.6,
        "estimated_cost": 1000.0,
        "popularity": 83,
        "coordinates": {"lat": 12.9124, "lon": 80.2312},
        "description": "High-capacity fuel center equipped with nitrogen tire stations, ultra-fast 60kW EV charging dispensers, and 24/7 convenience mart.",
        "special_feature": "Digital air pressure check and clean potable drinking water counter.",
        "tags": ["petrol_pumps", "highway_stop"]
    },

    # GOA
    {
        "id": "dest_goa_01",
        "name": "Palolem Crescent Beach & Dolphin Bay",
        "city": "Goa",
        "category": "attractions",
        "rating": 4.8,
        "estimated_cost": 250.0,
        "popularity": 95,
        "coordinates": {"lat": 15.0100, "lon": 74.0232},
        "description": "A tranquil mile-long crescent bay fringed by leaning coconut palms, calm swimmable waters, and picturesque eco-cottages.",
        "special_feature": "Gentle, non-turbulent waves ideal for standup paddleboarding, kayaking, and serene sunset gazing.",
        "tags": ["romantic", "kid_friendly", "attractions", "peaceful_break"]
    },
    {
        "id": "dest_goa_02",
        "name": "Fisherman's Wharf Goan Seafood Shack",
        "city": "Goa",
        "category": "food",
        "rating": 4.7,
        "estimated_cost": 900.0,
        "popularity": 93,
        "coordinates": {"lat": 15.1542, "lon": 73.9497},
        "description": "Riverside open-air dining featuring traditional Goan spiced butter garlic tiger prawns, fish curry rice, and bebinca desserts.",
        "special_feature": "Live acoustic Goan folk music overlooking wooden fishing trawlers on the Sal River.",
        "tags": ["food", "romantic", "senior_friendly"]
    },
    {
        "id": "dest_goa_03",
        "name": "Heritage Portuguese Villa & Boutique Stay",
        "city": "Goa",
        "category": "accommodation",
        "rating": 4.7,
        "estimated_cost": 3200.0,
        "popularity": 88,
        "coordinates": {"lat": 15.5008, "lon": 73.8344},
        "description": "Charming 18th-century restored Portuguese mansion with azulejo hand-painted tiles, breezy verandahs, and secluded garden plunge pool.",
        "special_feature": "Complimentary sunset cycling tours and personalized breakfast served in the orchard courtyard.",
        "tags": ["accommodation", "romantic", "peaceful_break"]
    },
    {
        "id": "dest_goa_04",
        "name": "NH-66 Highway Fuel & Sanitized Restroom Hub",
        "city": "Goa",
        "category": "restrooms",
        "rating": 4.4,
        "estimated_cost": 10.0,
        "popularity": 79,
        "coordinates": {"lat": 15.3500, "lon": 73.9100},
        "description": "Well-lit coastal highway utility stop with hygienic restrooms, drinking water ATM, and air conditioned waiting parlor.",
        "special_feature": "Designated wheelchair accessible ramp and dedicated women's washroom attendant.",
        "tags": ["restrooms", "petrol_pumps", "highway_stop"]
    },

    # MANALI & HIMACHAL
    {
        "id": "dest_mnl_01",
        "name": "Solang Valley Adventure & Glacier Meadow",
        "city": "Manali",
        "category": "attractions",
        "rating": 4.7,
        "estimated_cost": 650.0,
        "popularity": 97,
        "coordinates": {"lat": 32.3166, "lon": 77.1575},
        "description": "Breathtaking snow-clad alpine valley offering winter skiing, zorbing, ropeway cable car rides, and paragliding above pine forests.",
        "special_feature": "State-of-the-art cable car ropeway delivering birds-eye vistas of Pir Panjal snow peaks.",
        "tags": ["attractions", "kid_friendly", "adventure"]
    },
    {
        "id": "dest_mnl_02",
        "name": "Johnson's Cafe & Trout Bar",
        "city": "Manali",
        "category": "food",
        "rating": 4.6,
        "estimated_cost": 650.0,
        "popularity": 91,
        "coordinates": {"lat": 32.2472, "lon": 77.1882},
        "description": "Iconic wooden mountain bistro nestled inside an apple orchard, serving freshly caught Tirthan Valley wood-smoked river trout and wood-fired pizzas.",
        "special_feature": "Outdoor cozy bonfire seating with warm spiced apple cider and live jazz music.",
        "tags": ["food", "romantic"]
    },
    {
        "id": "dest_mnl_03",
        "name": "Pine Haven Alpine Timber Cottages",
        "city": "Manali",
        "category": "accommodation",
        "rating": 4.6,
        "estimated_cost": 2800.0,
        "popularity": 87,
        "coordinates": {"lat": 32.2396, "lon": 77.1887},
        "description": "Rustic deodar timber chalets featuring radiant floor heating, private balconies overlooking Beas River rapids, and complimentary mountain tea.",
        "special_feature": "Direct trail access to old deodar cedar forests without needing vehicle transit.",
        "tags": ["accommodation", "peaceful_break", "romantic"]
    },
    {
        "id": "dest_mnl_04",
        "name": "Atal Tunnel South Portal Clean Restroom & Fuel Point",
        "city": "Manali",
        "category": "restrooms",
        "rating": 4.8,
        "estimated_cost": 0.0,
        "popularity": 93,
        "coordinates": {"lat": 32.3639, "lon": 77.1328},
        "description": "Modern high-altitude BRO utility center providing free heated clean restrooms, emergency medical oxygen assistance, and vehicle inspection.",
        "special_feature": "Free emergency first-aid station and heated warm-water taps at 10,000 feet elevation.",
        "tags": ["restrooms", "senior_friendly", "highway_stop"]
    },

    # JAIPUR
    {
        "id": "dest_jpr_01",
        "name": "Amber Fort & Maota Lake Palace",
        "city": "Jaipur",
        "category": "attractions",
        "rating": 4.8,
        "estimated_cost": 250.0,
        "popularity": 98,
        "coordinates": {"lat": 26.9855, "lon": 75.8513},
        "description": "Magnificent red sandstone and marble fortress perched atop Cheel ka Teela, renowned for Sheesh Mahal (Mirror Palace) and royal courtyards.",
        "special_feature": "Electric golf-cart shuttle rides for comfortable ascent, ideal for seniors and families.",
        "tags": ["attractions", "heritage", "senior_friendly", "kid_friendly"]
    },
    {
        "id": "dest_jpr_02",
        "name": "Chokhi Dhani Ethnic Rajasthani Village & Thali",
        "city": "Jaipur",
        "category": "food",
        "rating": 4.6,
        "estimated_cost": 950.0,
        "popularity": 94,
        "coordinates": {"lat": 26.7667, "lon": 75.8333},
        "description": "Immersive cultural experience featuring traditional Kalbelia folk dance, puppet shows, camel rides, and endless royal dal baati churma thalis.",
        "special_feature": "Pure ghee authentic regional feast served with traditional royal hospitality.",
        "tags": ["food", "kid_friendly", "senior_friendly"]
    },
    {
        "id": "dest_jpr_03",
        "name": "Haveli Heritage Courtyard Hotel",
        "city": "Jaipur",
        "category": "accommodation",
        "rating": 4.7,
        "estimated_cost": 3100.0,
        "popularity": 89,
        "coordinates": {"lat": 26.9248, "lon": 75.8245},
        "description": "Authentic Rajput haveli with fresco-painted ceilings, tranquil lotus pond courtyards, and rooftop sunset view of Nahargarh Fort.",
        "special_feature": "Evening Kathak dance performance and puppet theatre exclusively for in-house guests.",
        "tags": ["accommodation", "romantic", "peaceful_break"]
    },
    {
        "id": "dest_jpr_04",
        "name": "Jaipur-Delhi Highway HPCL Comfort Rest Stop",
        "city": "Jaipur",
        "category": "petrol_pumps",
        "rating": 4.5,
        "estimated_cost": 500.0,
        "popularity": 82,
        "coordinates": {"lat": 27.1500, "lon": 75.9500},
        "description": "Air-conditioned express food court and fuel station with premium clean restrooms, EV fast-chargers, and highway security.",
        "special_feature": "Spotless sanitized restrooms with dedicated baby care lounge and sanitized filtered water.",
        "tags": ["petrol_pumps", "restrooms", "highway_stop"]
    }
]

def filter_and_sort_destinations(
    city: Optional[str] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    max_budget: Optional[float] = None,
    sort_by: Optional[str] = "popularity"
) -> List[Dict[str, Any]]:
    """Filter and sort destinations matching query parameters."""
    results = list(CURATED_DESTINATIONS)

    # 1. Filter by city if provided
    if city and city.strip():
        city_term = city.strip().lower()
        results = [d for d in results if city_term in d["city"].lower()]

    # 2. Filter by search keyword
    if search and search.strip():
        st = search.strip().lower()
        results = [
            d for d in results
            if st in d["name"].lower()
            or st in d["city"].lower()
            or st in d["description"].lower()
            or st in d["special_feature"].lower()
            or any(st in tag for tag in d.get("tags", []))
        ]

    # 3. Filter by category
    if category and category.strip():
        cat = category.strip().lower()
        results = [
            d for d in results
            if d["category"].lower() == cat or cat in d.get("tags", [])
        ]

    # 4. Filter by max budget
    if max_budget is not None and max_budget > 0:
        results = [d for d in results if d["estimated_cost"] <= max_budget]

    # 5. Sort by criteria
    if sort_by == "name_asc":
        results.sort(key=lambda x: x["name"].lower())
    elif sort_by == "rating_desc":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "estimated_cost_asc":
        results.sort(key=lambda x: x["estimated_cost"])
    else:  # 'popularity' or default
        results.sort(key=lambda x: x["popularity"], reverse=True)

    return results

async def get_destination_by_id(dest_id: str) -> Optional[Dict[str, Any]]:
    """Fetch rich details for a single selected destination combined concurrently with live weather and nearby options."""
    target = None
    for d in CURATED_DESTINATIONS:
        if d["id"] == dest_id:
            target = d
            break

    if not target:
        return None

    # Find nearby options in the same city (excluding self)
    city_places = [
        d for d in CURATED_DESTINATIONS
        if d["city"].lower() == target["city"].lower() and d["id"] != target["id"]
    ]

    nearby_options = []
    for p in city_places[:4]:
        nearby_options.append({
            "name": p["name"],
            "category": p["category"],
            "distance_km": round(abs(p["coordinates"]["lat"] - target["coordinates"]["lat"]) * 70.0 + 1.2, 1),
            "rating": p["rating"],
            "estimated_cost": p["estimated_cost"]
        })

    # Fetch real-time weather and AQI concurrently
    lat = target["coordinates"]["lat"]
    lon = target["coordinates"]["lon"]
    live_env = await fetch_weather_and_aqi(lat, lon)

    return {
        "destination": target,
        "nearby_options": nearby_options,
        "live_environment": live_env
    }
