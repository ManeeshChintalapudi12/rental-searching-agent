# RentWise AI

A portfolio-ready rental marketplace and AI assistant built as a production-style monorepo. The app is organized by responsibility: UI in the frontend folder, backend APIs in the backend folder, and AI/RAG logic in the agentic folder.

## Product summary

- Frontend: Next.js UI for searching apartments and vehicles by city
- Backend: FastAPI service for location search, public rental feeds, and rental APIs
- Agentic layer: RAG and LangGraph-style orchestration for market-aware answers
- Data path: OpenStreetMap geocoding plus no-key public fallback data for demo-ready U.S. searches

## Repository structure

```text
rental-searching-app/
├── frontend/          # Next.js app and UI logic
├── backend/           # FastAPI backend, providers, models, and tests
├── agentic/           # AI/RAG and LangGraph workflow logic
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── package.json
├── package-lock.json
└── .venv/
```

## Local development

### 1) Install root dependencies

```powershell
cd "c:\rental-searching-app"
npm install
```

### 2) Start the app locally

```powershell
cd "c:\rental-searching-app"
npm run dev
```

This starts the frontend and backend together using the final folder structure.

### 3) Run API tests

```powershell
cd "c:\rental-searching-app"
python -m pytest -q backend/tests
```

### Useful URLs

- http://localhost:3000
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/public-rentals?city=Danville&state=CA&limit=5
- http://127.0.0.1:8000/api/live-feed

## Deployment readiness

This repo is aligned for real product workflows:

- clean frontend/backend/agentic separation
- environment-based config via `.env`
- Docker support for local stack orchestration
- searchable market intelligence with a no-key fallback path

### Frontend deployment

Use Vercel with:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url
```

### Backend deployment

Use Render or Railway and expose the FastAPI app on port 8000.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up --build
```

## AI story

The application includes:

- retrieval-augmented generation
- vector document ingestion
- LangGraph-style orchestration pattern
- market-aware answers for U.S. rental searches

## Real-data path

The current implementation uses a no-key public fallback:

- OpenStreetMap Nominatim geocoding
- U.S. city/state matching for searchable markets
- public market feed for demo-ready results
- adapter-ready structure for future licensed data APIs
