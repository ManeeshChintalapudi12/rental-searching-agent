# RentWise AI

A rental search app with apartment and vehicle comparison, backed by a FastAPI API and a Next.js frontend.

## Local setup

### Frontend

```bash
cd rental-app
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

## Search

The app supports searching by location text such as "Frisco", "Dallas", or other U.S. city names.

## Main routes

- Frontend: http://localhost:3000
- API health: http://localhost:8000/health
- Listings: http://localhost:8000/api/listings?mode=apartments&q=Frisco
