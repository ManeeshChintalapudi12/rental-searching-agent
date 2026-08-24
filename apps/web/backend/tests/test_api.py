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
