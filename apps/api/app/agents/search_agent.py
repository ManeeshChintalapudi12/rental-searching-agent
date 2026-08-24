from app.models import RentalIntent, SearchRequest, SearchResponse
from app.services.search_service import SearchService


class SearchAgent:
    """Executes only validated provider searches; it never generates listings."""

    def __init__(self, service: SearchService) -> None:
        self.service = service

    async def run(self, intent: RentalIntent) -> SearchResponse:
        return await self.service.search(SearchRequest(**intent.model_dump(exclude={"missing_fields"})))
