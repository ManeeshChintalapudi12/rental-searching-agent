# RentWise AI — Phase 1

Responsive rental-search application for apartments and vehicles. Phase 1 provides the interactive UI. Phase 2 adds a FastAPI backend, normalized provider contract, mock marketplace data, search service, tests, and PostgreSQL development configuration.

## Requirements

- Node.js 20.9 or newer
- VS Code

## Run in VS Code

1. Extract this ZIP.
2. Open the `RentWise-AI` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run:

```powershell
npm install
npm run dev
```

5. Open `http://localhost:3000` in your browser.

Stop the app with `Ctrl+C`.

## Run the Phase 2 backend

Open a second VS Code terminal:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

Open the API documentation at `http://localhost:8000/docs`.

Test the backend:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

The health endpoint is `http://localhost:8000/health`. The normalized search endpoint is `POST http://localhost:8000/api/v1/search`.

## Main files

- `app/page.tsx` — UI, sample data, and interactions
- `app/globals.css` — responsive visual design
- `app/layout.tsx` — application metadata and root layout
- `backend/app/main.py` — FastAPI application and routes
- `backend/app/models.py` — normalized rental request/response models
- `backend/app/providers/` — provider adapter contract and mock provider
- `backend/app/services/` — search orchestration service
- `backend/tests/` — API tests
- `docker-compose.yml` — local PostgreSQL service for the next milestone

## Current limitation

Listings and prices still use mock provider data. The next Phase 2 milestone will connect the frontend to this API, add PostgreSQL persistence, and introduce the LLM requirement-extraction endpoint.
