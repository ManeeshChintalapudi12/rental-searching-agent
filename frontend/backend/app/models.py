from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class RentalType(StrEnum):
    APARTMENT = "apartment"
    VEHICLE = "vehicle"


class Money(BaseModel):
    amount: float = Field(ge=0)
    currency: str = "USD"


class Location(BaseModel):
    label: str
    city: str
    state: str
    latitude: float
    longitude: float


class RentalListing(BaseModel):
    id: str
    provider: str
    provider_listing_id: str
    rental_type: RentalType
    title: str
    description: str
    location: Location
    image_url: str
    base_price: Money
    total_price: Money
    price_period: str
    mandatory_fees: Money
    rating: float = Field(ge=0, le=5)
    review_count: int = Field(ge=0)
    features: list[str]
    available_from: date | None = None
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchRequest(BaseModel):
    rental_type: RentalType
    location: str = Field(min_length=2)
    start_date: date | None = None
    end_date: date | None = None
    max_total_price: float | None = Field(default=None, ge=0)
    features: list[str] = []
    sort_by: str = "recommended"


class SearchResponse(BaseModel):
    query: SearchRequest
    count: int
    listings: list[RentalListing]
    providers_queried: list[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
