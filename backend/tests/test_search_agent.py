"""SearchAgent unit tests — no HTTP layer, just the agent + mock provider."""

import asyncio
from datetime import date

from app.agents.search_agent import SearchAgent
from app.models import RentalIntent, RentalType
from app.providers import MockRentalProvider
from app.services.search_service import SearchService


def _run(coro):
    return asyncio.run(coro)


def test_reversed_date_range_from_intent_is_dropped_not_fatal() -> None:
    """A bad range produced by intent parsing must not crash the chat flow."""
    agent = SearchAgent(SearchService(providers=[MockRentalProvider()]))
    intent = RentalIntent(
        rental_type=RentalType.APARTMENT,
        location="Frisco, TX",
        start_date=date(2026, 12, 10),
        end_date=date(2026, 12, 5),
    )
    result = _run(agent.run(intent))
    assert result.count >= 1
    assert result.query.start_date is None
    assert result.query.end_date is None


def test_valid_date_range_from_intent_is_kept() -> None:
    agent = SearchAgent(SearchService(providers=[MockRentalProvider()]))
    intent = RentalIntent(
        rental_type=RentalType.APARTMENT,
        location="Frisco, TX",
        start_date=date(2026, 12, 5),
        end_date=date(2026, 12, 10),
    )
    result = _run(agent.run(intent))
    assert result.query.start_date == date(2026, 12, 5)
    assert result.query.end_date == date(2026, 12, 10)
