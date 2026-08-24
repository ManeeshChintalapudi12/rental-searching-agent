from openai import AsyncOpenAI

from app.config import Settings
from app.models import Recommendation, RentalIntent, RentalListing


class ResponseAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def run(
        self, intent: RentalIntent, listings: list[RentalListing], recommendations: list[Recommendation]
    ) -> str:
        if intent.missing_fields:
            return f"What {', '.join(intent.missing_fields)} should I search near?"
        if not listings:
            return "I couldn't find a verified match. Try increasing the budget or removing one must-have."
        facts = [
            {
                "id": item.id, "title": item.title,
                "total": item.total_price.model_dump(), "fees": item.mandatory_fees.model_dump(),
                "rating": item.rating, "features": item.features,
            } for item in listings
        ]
        if self.client:
            response = await self.client.responses.create(
                model=self.settings.openai_model,
                instructions=(
                    "You are RentWise AI. Recommend only from LISTING_FACTS. Cite every factual "
                    "claim with the listing ID in square brackets. Never change a price, fee, rating, "
                    "feature, or availability. Be concise and explain total cost."
                ),
                input=f"USER_INTENT={intent.model_dump_json()}\nLISTING_FACTS={facts}\nRANKING={recommendations}",
            )
            return response.output_text
        top = recommendations[0]
        listing = next(item for item in listings if item.id == top.listing_id)
        return (
            f"The best verified match is {listing.title} at ${listing.total_price.amount:,.0f} total "
            f"including ${listing.mandatory_fees.amount:,.0f} in mandatory fees [{listing.id}]. "
            f"It has a {listing.rating}/5 rating and a {top.deal_score}/100 deal score."
        )
