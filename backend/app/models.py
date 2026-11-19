from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


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
    features: list[str] = Field(default_factory=list)
    sort_by: str = "recommended"

    @model_validator(mode="after")
    def check_date_range(self) -> "SearchRequest":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must be on or after start_date")
        return self


class SearchResponse(BaseModel):
    query: SearchRequest
    count: int
    listings: list[RentalListing]
    providers_queried: list[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RentalIntent(BaseModel):
    rental_type: RentalType
    location: str
    start_date: date | None = None
    end_date: date | None = None
    max_total_price: float | None = None
    features: list[str] = Field(default_factory=list)
    sort_by: str = "recommended"
    missing_fields: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    listing_id: str
    reason: str
    verified_total: Money
    deal_score: float = Field(ge=0, le=100)


class AgentTrace(BaseModel):
    agent: str
    status: str
    detail: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    intent: RentalIntent
    listings: list[RentalListing]
    recommendations: list[Recommendation]
    citations: list[str]
    grounded: bool
    needs_clarification: bool
    agent_trace: list[AgentTrace]
