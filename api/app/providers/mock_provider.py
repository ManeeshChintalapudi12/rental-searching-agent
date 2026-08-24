from datetime import date

from app.models import Location, Money, RentalListing, RentalType, SearchRequest
from app.providers.base import RentalProvider


class MockRentalProvider(RentalProvider):
    name = "mock-marketplace"

    def __init__(self) -> None:
        frisco = Location(
            label="Frisco, Texas", city="Frisco", state="TX",
            latitude=33.1507, longitude=-96.8236,
        )
        dfw = Location(
            label="DFW Airport", city="Dallas", state="TX",
            latitude=32.8998, longitude=-97.0403,
        )
        self._listings = [
            RentalListing(
                id="apt-001", provider=self.name, provider_listing_id="A001",
                rental_type=RentalType.APARTMENT, title="The Maxwell at Frisco",
                description="1 bed · 1 bath · 742 sq ft", location=frisco,
                image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267d",
                base_price=Money(amount=1485), total_price=Money(amount=1554),
                mandatory_fees=Money(amount=69), price_period="month", rating=4.8,
                review_count=126, features=["Gym", "Pool", "Parking"],
                available_from=date(2026, 9, 1),
            ),
            RentalListing(
                id="apt-002", provider=self.name, provider_listing_id="A002",
                rental_type=RentalType.APARTMENT, title="Frisco Square Lofts",
                description="Studio · 1 bath · 611 sq ft", location=frisco,
                image_url="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
                base_price=Money(amount=1325), total_price=Money(amount=1407),
                mandatory_fees=Money(amount=82), price_period="month", rating=4.5,
                review_count=78, features=["Walkable", "Coworking", "Parking"],
                available_from=date(2026, 9, 1),
            ),
            RentalListing(
                id="car-001", provider=self.name, provider_listing_id="V001",
                rental_type=RentalType.VEHICLE, title="Toyota RAV4 or similar",
                description="Compact SUV · 5 seats · 3 bags", location=dfw,
                image_url="https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6",
                base_price=Money(amount=240), total_price=Money(amount=326),
                mandatory_fees=Money(amount=86), price_period="trip", rating=4.7,
                review_count=841,
                features=["Unlimited miles", "Free cancellation", "Automatic"],
            ),
            RentalListing(
                id="car-002", provider=self.name, provider_listing_id="V002",
                rental_type=RentalType.VEHICLE, title="Hyundai Elantra or similar",
                description="Midsize · 5 seats · 2 bags", location=frisco,
                image_url="https://images.unsplash.com/photo-1553440569-bcc63803a83d",
                base_price=Money(amount=195), total_price=Money(amount=267),
                mandatory_fees=Money(amount=72), price_period="trip", rating=4.5,
                review_count=362,
                features=["Unlimited miles", "Free cancellation", "Automatic"],
            ),
        ]

    async def search(self, request: SearchRequest) -> list[RentalListing]:
        listings = [item for item in self._listings if item.rental_type == request.rental_type]
        if request.max_total_price is not None:
            listings = [item for item in listings if item.total_price.amount <= request.max_total_price]
        if request.features:
            wanted = {feature.casefold() for feature in request.features}
            listings = [
                item for item in listings
                if wanted.issubset({feature.casefold() for feature in item.features})
            ]
        if request.sort_by == "lowest_total":
            listings.sort(key=lambda item: item.total_price.amount)
        elif request.sort_by == "highest_rated":
            listings.sort(key=lambda item: item.rating, reverse=True)
        return listings

    async def get_listing(self, listing_id: str) -> RentalListing | None:
        return next((item for item in self._listings if item.id == listing_id), None)
