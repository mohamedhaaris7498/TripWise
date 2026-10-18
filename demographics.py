def classify_age_bracket(age: int) -> str:
    """
    Classify user into demographic age brackets to drive smart travel recommendations:
    - Youth/Student (< 25): Budget-conscious, adventure, vibrant food, nightlife, public transit.
    - Adult (25-59): Balanced pacing, cultural & scenic, mid-tier comfort, dining.
    - Senior/Old-Age (60+): Relaxed pacing, flat terrain/accessible spots, close medical & clean restrooms.
    """
    if age < 25:
        return "Youth/Student"
    elif age < 60:
        return "Adult"
    else:
        return "Senior/Old-Age"

def get_age_bracket_preferences(bracket: str) -> dict:
    """Return recommendation tuning flags and pacing profile for each age bracket."""
    if bracket == "Youth/Student":
        return {
            "pacing": "fast-paced & energetic",
            "preferred_categories": ["attractions", "nightlife", "adventure", "food", "budget_stays"],
            "max_daily_walking_km": 12,
            "transport_preference": "Public transit, bikes, shared cabs",
            "must_have_amenities": ["wifi", "budget_food"]
        }
    elif bracket == "Senior/Old-Age":
        return {
            "pacing": "slow & relaxed",
            "preferred_categories": ["senior_friendly", "cultural", "parks", "peaceful_break", "restrooms"],
            "max_daily_walking_km": 3.5,
            "transport_preference": "Direct AC cab, minimal stairs, flat surfaces",
            "must_have_amenities": ["clean_restrooms", "wheelchair_accessible", "medical_proximity"]
        }
    else:  # Adult
        return {
            "pacing": "moderate & comprehensive",
            "preferred_categories": ["attractions", "food", "accommodation", "cultural", "scenic"],
            "max_daily_walking_km": 7,
            "transport_preference": "Comfort cab, rental car, express train",
            "must_have_amenities": ["clean_restrooms", "parking", "quality_stays"]
        }
