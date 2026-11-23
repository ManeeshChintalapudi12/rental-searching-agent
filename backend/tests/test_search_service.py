"""SearchService unit tests — provider aggregation behaviour."""

import asyncio

from app.models import RentalType, SearchRequest
from app.providers import MockRentalProvider
from app.providers.base import RentalProvider
from app.services.search_service import SearchService


def _run(coro):
    return asyncio.run(coro)


class _DuplicateProvider(RentalProvider):
    """Replays the mock provider's apartment listings under a second name,
    simulating an aggregator that mirrors the source marketplace."""

    name = "aggregator-mirror"

    def __init__(self, source: MockRentalProvider) -> None:
        self._source = source

    async def search(self, request):
        return await self._source.search(request)

    async def get_listing(self, listing_id):
        return await self._source.get_listing(listing_id)


def test_duplicate_listings_across_providers_are_deduplicated() -> None:
    mock = MockRentalProvider()
    service = SearchService(providers=[mock, _DuplicateProvider(mock)])
    request = SearchRequest(rental_type=RentalType.APARTMENT, location="Frisco, TX")
    result = _run(service.search(request))
    # The mirror replays both apartments, so without dedup this would be 4.
    assert result.count == 2
    assert [listing.id for listing in result.listings] == ["apt-001", "apt-002"]
    # The source marketplace's copy wins: first provider's listings are kept.
    assert all(listing.provider == "mock-marketplace" for listing in result.listings)


def test_same_provider_listed_twice_collapses_duplicates() -> None:
    mock = MockRentalProvider()
    service = SearchService(providers=[mock, mock])
    request = SearchRequest(rental_type=RentalType.APARTMENT, location="Frisco, TX")
    result = _run(service.search(request))
    assert result.count == 2
    assert [listing.id for listing in result.listings] == ["apt-001", "apt-002"]
    assert result.providers_queried == ["mock-marketplace", "mock-marketplace"]
