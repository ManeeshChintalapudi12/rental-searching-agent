from app.models import RentalListing, SearchRequest, SearchResponse
from app.providers.base import RentalProvider


class SearchService:
    def __init__(self, providers: list[RentalProvider]) -> None:
        self.providers = providers

    async def search(self, request: SearchRequest) -> SearchResponse:
        results: list[RentalListing] = []
        for provider in self.providers:
            results.extend(await provider.search(request))

        # Same listing can come back from more than one provider (e.g. an
        # aggregator and the source marketplace). Keep the first occurrence
        # of each provider_listing_id so callers never see the same unit
        # twice; the source marketplace's copy wins because providers are
        # queried in priority order.
        seen: set[str] = set()
        unique: list[RentalListing] = []
        for listing in results:
            if listing.provider_listing_id in seen:
                continue
            seen.add(listing.provider_listing_id)
            unique.append(listing)
        results = unique

        # Phase 2 extension point: normalize currencies and compute deal
        # scores before returning results.
        return SearchResponse(
            query=request,
            count=len(results),
            listings=results,
            providers_queried=[provider.name for provider in self.providers],
        )

    async def get_listing(self, listing_id: str) -> RentalListing | None:
        for provider in self.providers:
            listing = await provider.get_listing(listing_id)
            if listing:
                return listing
        return None
