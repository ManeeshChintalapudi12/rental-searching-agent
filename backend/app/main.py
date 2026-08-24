from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title=os.getenv("APP_NAME", "Rental Search API"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LISTINGS = [
    {
        "id": 1,
        "mode": "apartments",
        "title": "The Maxwell at Frisco",
        "detail": "1 bed · 1 bath · 742 sq ft",
        "place": "Warren Pkwy, Frisco · 1.8 mi",
        "image": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267d?auto=format&fit=crop&w=900&q=85",
        "price": 1485,
        "total": 1554,
        "period": "/mo",
        "rating": "4.8",
        "provider": "RentCafe",
        "tags": ["Gym", "Pool", "Parking"],
        "badge": "Best overall",
        "fees": "$69 mandatory fees included",
        "xy": [23, 38],
    },
    {
        "id": 2,
        "mode": "apartments",
        "title": "Cypress Lake at Stonebriar",
        "detail": "1 bed · 1 bath · 785 sq ft",
        "place": "Warren Pkwy, Frisco · 2.3 mi",
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=900&q=85",
        "price": 1520,
        "total": 1580,
        "period": "/mo",
        "rating": "4.6",
        "provider": "Apartments.com",
        "tags": ["Pet friendly", "Garage", "Pool"],
        "badge": "1 month free",
        "fees": "$60 monthly fees included",
        "xy": [61, 25],
    },
    {
        "id": 3,
        "mode": "apartments",
        "title": "Frisco Square Lofts",
        "detail": "Studio · 1 bath · 611 sq ft",
        "place": "Hickory St, Frisco · 0.7 mi",
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=900&q=85",
        "price": 1325,
        "total": 1407,
        "period": "/mo",
        "rating": "4.5",
        "provider": "Zillow",
        "tags": ["Walkable", "Coworking", "Parking"],
        "badge": "Lowest total",
        "fees": "$82 mandatory fees included",
        "xy": [43, 59],
    },
    {
        "id": 4,
        "mode": "vehicles",
        "title": "Toyota RAV4 or similar",
        "detail": "Compact SUV · 5 seats · 3 bags",
        "place": "DFW Airport · At terminal",
        "image": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?auto=format&fit=crop&w=900&q=85",
        "price": 48,
        "total": 326,
        "period": "/day",
        "rating": "4.7",
        "provider": "Budget",
        "tags": ["Unlimited miles", "Free cancellation", "Automatic"],
        "badge": "Best value",
        "fees": "$86 taxes & fees included · 5 days",
        "xy": [24, 42],
    },
    {
        "id": 5,
        "mode": "vehicles",
        "title": "Nissan Rogue or similar",
        "detail": "Midsize SUV · 5 seats · 4 bags",
        "place": "DFW Airport · At terminal",
        "image": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=900&q=85",
        "price": 51,
        "total": 349,
        "period": "/day",
        "rating": "4.8",
        "provider": "Enterprise",
        "tags": ["Unlimited miles", "Pay at pickup", "Automatic"],
        "badge": "Top rated",
        "fees": "$94 taxes & fees included · 5 days",
        "xy": [60, 28],
    },
    {
        "id": 6,
        "mode": "vehicles",
        "title": "Hyundai Elantra or similar",
        "detail": "Midsize · 5 seats · 2 bags",
        "place": "Frisco Downtown · 1.2 mi",
        "image": "https://images.unsplash.com/photo-1553440569-bcc63803a83d?auto=format&fit=crop&w=900&q=85",
        "price": 39,
        "total": 267,
        "period": "/day",
        "rating": "4.5",
        "provider": "Hertz",
        "tags": ["Unlimited miles", "Free cancellation", "Automatic"],
        "badge": "Lowest total",
        "fees": "$72 taxes & fees included · 5 days",
        "xy": [42, 61],
    },
]


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "rental-search-api"}


@app.get("/")
def root():
    return {"message": "Rental Search API is running"}


@app.get("/api/listings")
def get_listings(
    mode: str | None = Query(default=None),
    q: str | None = Query(default=None, alias="q"),
    location: str | None = Query(default=None, alias="location"),
):
    results = LISTINGS

    if mode:
        results = [item for item in results if item["mode"] == mode]

    search_term = (q or location or "").strip().lower()
    if search_term:
        results = [
            item
            for item in results
            if search_term in " ".join([
                item.get("title", ""),
                item.get("detail", ""),
                item.get("place", ""),
                item.get("provider", ""),
                *item.get("tags", []),
            ]).lower()
        ]

    return results
