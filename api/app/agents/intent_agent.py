import re
from datetime import date

from openai import AsyncOpenAI

from app.config import Settings
from app.models import RentalIntent, RentalType


class IntentAgent:
    """Turns natural language into a validated rental-search intent."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def run(self, message: str, previous: RentalIntent | None = None) -> RentalIntent:
        if self.client:
            context = previous.model_dump_json() if previous else "No previous search."
            response = await self.client.responses.parse(
                model=self.settings.openai_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Extract rental search requirements. Support long-term apartments and "
                            "rental vehicles. Never invent dates or budgets. Put required unknowns "
                            "in missing_fields. Use previous context only when the user is refining it."
                        ),
                    },
                    {"role": "user", "content": f"Previous: {context}\nCurrent: {message}"},
                ],
                text_format=RentalIntent,
            )
            if response.output_parsed:
                return response.output_parsed
        return self._fallback(message, previous)

    def _fallback(self, message: str, previous: RentalIntent | None) -> RentalIntent:
        text = message.casefold()
        rental_type = (
            RentalType.VEHICLE if re.search(r"\b(car|suv|vehicle|van|truck)\b", text)
            else RentalType.APARTMENT
        )
        budget_match = re.search(r"(?:under|max(?:imum)?|budget(?: of)?)\s*\$?([\d,]+)", text)
        budget = float(budget_match.group(1).replace(",", "")) if budget_match else None
        location = "DFW Airport" if "dfw" in text else "Frisco, TX" if "frisco" in text else ""
        features = [
            feature for keyword, feature in {
                "parking": "Parking", "gym": "Gym", "pool": "Pool",
                "pet": "Pet friendly", "unlimited": "Unlimited miles",
                "automatic": "Automatic", "free cancellation": "Free cancellation",
            }.items() if keyword in text
        ]
        if previous:
            location = location or previous.location
            budget = budget if budget is not None else previous.max_total_price
            features = features or previous.features
            if not re.search(r"\b(apartment|bedroom|studio|car|suv|vehicle|van|truck)\b", text):
                rental_type = previous.rental_type
        missing = [] if location else ["location"]
        return RentalIntent(
            rental_type=rental_type, location=location or "Unknown",
            max_total_price=budget, features=features,
            sort_by="lowest_total" if "cheapest" in text or "lowest" in text else "recommended",
            missing_fields=missing,
        )
