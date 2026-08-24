from abc import ABC, abstractmethod

from app.models import RentalListing, SearchRequest


class RentalProvider(ABC):
    """Contract every live marketplace adapter must implement."""

    name: str

    @abstractmethod
    async def search(self, request: SearchRequest) -> list[RentalListing]:
        raise NotImplementedError

    @abstractmethod
    async def get_listing(self, listing_id: str) -> RentalListing | None:
        raise NotImplementedError
