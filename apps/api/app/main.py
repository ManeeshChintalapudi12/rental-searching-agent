import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents import RentalAssistantOrchestrator
from app.ai_stack import RentalAIStack
from app.config import get_settings
from app.models import ChatRequest, ChatResponse, RentalListing, SearchRequest, SearchResponse
from app.providers import MockRentalProvider
from app.services.search_service import SearchService

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Normalized rental search API for RentWise AI.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_service = SearchService(providers=[MockRentalProvider()])
assistant = RentalAssistantOrchestrator(settings=settings, search_service=search_service)
ai_stack = RentalAIStack()
ai_stack.ingest([
    {
        "id": "doc-danville",
        "text": "Danville, CA has a strong family-oriented rental market with steady demand and competitive pricing in the Bay Area.",
        "metadata": {"city": "Danville", "state": "CA"},
    },
    {
        "id": "doc-seattle",
        "text": "Seattle, WA has competitive apartment pricing driven by major employers and a tight rental supply near downtown.",
        "metadata": {"city": "Seattle", "state": "WA"},
    },
    {
        "id": "doc-frisco",
        "text": "Frisco, TX sees high apartment demand due to suburban growth, transportation access, and a strong tenant pipeline.",
        "metadata": {"city": "Frisco", "state": "TX"},
    },
])

CITY_DATA: dict[str, dict[str, str]] = {
    "danville": {"city": "Danville", "state": "CA", "lat": "37.8216", "lon": "-121.9997"},
    "seattle": {"city": "Seattle", "state": "WA", "lat": "47.6062", "lon": "-122.3321"},
    "miami": {"city": "Miami", "state": "FL", "lat": "25.7617", "lon": "-80.1918"},
    "austin": {"city": "Austin", "state": "TX", "lat": "30.2672", "lon": "-97.7431"},
    "denver": {"city": "Denver", "state": "CO", "lat": "39.7392", "lon": "-104.9903"},
    "new york": {"city": "New York", "state": "NY", "lat": "40.7128", "lon": "-74.0060"},
    "frisco": {"city": "Frisco", "state": "TX", "lat": "33.1507", "lon": "-96.8236"},
    "los angeles": {"city": "Los Angeles", "state": "CA", "lat": "34.0522", "lon": "-118.2437"},
    "phoenix": {"city": "Phoenix", "state": "AZ", "lat": "33.4484", "lon": "-112.0740"},
    "san jose": {"city": "San Jose", "state": "CA", "lat": "37.3382", "lon": "-121.8863"},
}


def _normalize_city_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


async def _geo_lookup(query: str) -> list[dict[str, Any]]:
    base_query = query.strip()
    if not base_query:
        return []

    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "RentWiseAI/1.0"}) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": base_query,
                    "format": "jsonv2",
                    "limit": 5,
                    "countrycodes": "us",
                    "addressdetails": 1,
                },
            )
        if response.status_code == 200:
            payload = response.json()
            matches: list[dict[str, Any]] = []
            for item in payload:
                address = item.get("address") or {}
                city = address.get("city") or address.get("town") or address.get("village") or item.get("name")
                state = address.get("state")
                if city and state:
                    matches.append({
                        "city": city,
                        "state": state,
                        "display_name": item.get("display_name", f"{city}, {state}"),
                        "lat": item.get("lat"),
                        "lon": item.get("lon"),
                    })
            if matches:
                return matches
    except Exception:
        pass

    city_name = base_query.split(",", 1)[0].strip()
    normalized = _normalize_city_name(city_name)
    matches = []
    for key, data in CITY_DATA.items():
        if normalized in key or key in normalized:
            matches.append({
                "city": data["city"],
                "state": data["state"],
                "display_name": f"{data['city']}, {data['state']}",
                "lat": data["lat"],
                "lon": data["lon"],
            })
    if matches:
        return matches

    fallback = [{
        "city": city_name or "Unknown",
        "state": base_query.split(",", 1)[1].strip() if "," in base_query else "US",
        "display_name": base_query,
        "lat": "0.0",
        "lon": "0.0",
    }]
    return fallback


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.app_name, "version": "0.2.0"}


@app.get("/api/location-search")
async def location_search(query: str = Query(..., min_length=1)):
    return await _geo_lookup(query)


@app.get("/api/public-rentals")
async def public_rentals(city: str = Query(..., min_length=2), state: str = Query("US"), limit: int = Query(5, ge=1, le=20)):
    normalized_city = city.strip()
    canonical = _normalize_city_name(normalized_city)
    city_lookup = CITY_DATA.get(canonical)
    if city_lookup is None:
        city_lookup = {"city": normalized_city, "state": state.upper() or "US", "lat": "0.0", "lon": "0.0"}

    prices = [2200, 2450, 2680, 2900, 3100, 3300, 3600, 3950, 4200]
    results = []
    for index in range(min(limit, len(prices))):
        price = prices[index] + (index * 90)
        results.append({
            "title": f"{city_lookup['city']} Studio / 1BR Rental",
            "location": f"{index + 1} block near downtown {city_lookup['city']}, {city_lookup['state']}",
            "price": f"${price}/mo",
            "source": "Public market feed",
        })

    return {
        "city": city_lookup["city"],
        "state": city_lookup["state"],
        "results": results,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


@app.get("/api/ai/rag")
async def ai_rag(question: str = Query(..., min_length=2)):
    return ai_stack.query(question)


@app.get("/api/live-feed")
async def live_feed():
    async def event_generator():
        while True:
            payload = {
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "status": "live",
                "city": "Danville, CA",
                "inventory": 4,
                "avg_price": 4200,
                "delta": "+2.1%",
                "headline": "Live market pulse is updating",
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post(f"{settings.api_prefix}/search", response_model=SearchResponse, tags=["rentals"])
async def search(request: SearchRequest) -> SearchResponse:
    return await search_service.search(request)


@app.get(
    f"{settings.api_prefix}/listings/{{listing_id}}",
    response_model=RentalListing,
    tags=["rentals"],
)
async def listing_details(listing_id: str) -> RentalListing:
    listing = await search_service.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Rental listing not found")
    return listing


@app.post(f"{settings.api_prefix}/chat", response_model=ChatResponse, tags=["assistant"])
async def chat(request: ChatRequest) -> ChatResponse:
    return await assistant.run(request)
