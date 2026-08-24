from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import RentalListing, SearchRequest, SearchResponse
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
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_service = SearchService(providers=[MockRentalProvider()])


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.app_name, "version": "0.2.0"}


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
