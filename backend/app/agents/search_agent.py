from app.models import RentalIntent, SearchRequest, SearchResponse
from app.services.search_service import SearchService


class SearchAgent:
    """Executes only validated provider searches; it never generates listings."""

    def __init__(self, service: SearchService) -> None:
        self.service = service

    async def run(self, intent: RentalIntent) -> SearchResponse:
        data = intent.model_dump(exclude={"missing_fields"})
        # A reversed date range from intent parsing is not a user error worth
        # failing the whole chat over: drop the dates and search unfiltered
        # rather than letting SearchRequest validation raise inside the
        # orchestrator. Direct API callers still get a 422 (see models.py).
        if (
            data.get("start_date") is not None
            and data.get("end_date") is not None
            and data["end_date"] < data["start_date"]
        ):
            data["start_date"] = None
            data["end_date"] = None
        return await self.service.search(SearchRequest(**data))
