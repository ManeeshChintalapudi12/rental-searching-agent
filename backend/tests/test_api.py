from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_apartments_by_total_price() -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "rental_type": "apartment",
            "location": "Frisco, TX",
            "max_total_price": 1450,
            "sort_by": "lowest_total",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["listings"][0]["id"] == "apt-002"


def test_listing_not_found() -> None:
    response = client.get("/api/v1/listings/missing")
    assert response.status_code == 404


def test_chat_uses_grounded_fallback_without_api_key() -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "Find the cheapest apartment in Frisco under $1500"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is True
    assert payload["citations"] == ["apt-002"]
    assert payload["recommendations"][0]["listing_id"] == "apt-002"
    assert "$1,407" in payload["answer"]


def test_chat_requests_missing_location() -> None:
    response = client.post("/api/v1/chat", json={"message": "Find me an SUV"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["needs_clarification"] is True
    assert "location" in payload["intent"]["missing_fields"]


def test_location_search_and_public_rentals_endpoints() -> None:
    geo = client.get("/api/location-search", params={"query": "Danville, CA"})
    assert geo.status_code == 200
    locations = geo.json()
    assert isinstance(locations, list)
    assert len(locations) >= 1
    assert locations[0]["city"] == "Danville"

    rentals = client.get("/api/public-rentals", params={"city": "Danville", "state": "CA", "limit": 3})
    assert rentals.status_code == 200
    payload = rentals.json()
    assert payload["city"] == "Danville"
    assert payload["state"] == "CA"
    assert len(payload["results"]) >= 1
