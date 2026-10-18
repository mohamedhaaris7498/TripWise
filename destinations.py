from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.schemas.destination import DestinationListResponse, DestinationDetailResponse
from app.services.places_service import filter_and_sort_destinations, get_destination_by_id
from app.services.cache_service import cache

router = APIRouter(prefix="/api/destinations", tags=["Destinations Discovery & Search"])

@router.get("", response_model=DestinationListResponse)
async def list_destinations(
    city: Optional[str] = Query(None, description="Filter by city (e.g. Chennai, Goa, Manali, Jaipur)"),
    search: Optional[str] = Query(None, description="Search keyword in destination name, description or tags"),
    category: Optional[str] = Query(
        None,
        description="Category filter: attractions, food, accommodation, restrooms, petrol_pumps, senior_friendly, kid_friendly, romantic"
    ),
    max_budget: Optional[float] = Query(None, ge=0.0, description="Maximum estimated price"),
    sort_by: Optional[str] = Query(
        "popularity",
        description="Sorting order: popularity, rating_desc, name_asc, estimated_cost_asc"
    )
):
    """
    Core Destination Discovery, Search, Filter & Sort.
    Zero-lag caching returns instant responses for repeated queries.
    """
    cache_key = f"dest_query:{city}:{search}:{category}:{max_budget}:{sort_by}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return DestinationListResponse(
            destinations=cached_data,
            total=len(cached_data),
            cached=True
        )

    results = filter_and_sort_destinations(
        city=city,
        search=search,
        category=category,
        max_budget=max_budget,
        sort_by=sort_by
    )

    # Cache query result for 15 minutes
    cache.set(cache_key, results, ttl=900)

    return DestinationListResponse(
        destinations=results,
        total=len(results),
        cached=False
    )

@router.get("/{destination_id}", response_model=DestinationDetailResponse)
async def get_destination_details(destination_id: str):
    """
    Return rich details for a single selected destination:
    - Coordinates, description, and 'What is special about this place'
    - Nearby food, stays, and highway stops
    - Live temperature, humidity % and Air Quality Index (AQI) computed concurrently.
    """
    details = await get_destination_by_id(destination_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID '{destination_id}' was not found in the travel catalog."
        )

    return DestinationDetailResponse(**details)
