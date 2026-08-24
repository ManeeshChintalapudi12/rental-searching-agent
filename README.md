# RentWise AI

A portfolio-ready rental marketplace and AI assistant built as a production-style monorepo. It combines a premium search UI, an AI-enabled rental insights workflow, and a U.S. city search flow that works without a paid vendor key.

## Product summary

- Web app: Next.js frontend for the search experience
- API: FastAPI backend for rental search, geocoding, and AI routes
- AI layer: retrieval and LangGraph-style orchestration for market-aware answers
- Data path: OpenStreetMap geocoding plus a public fallback feed for demo-ready usage

## Repository

- GitHub: https://github.com/ManeeshChintalapudi12/rental-searching-agent.git

## Monorepo structure

```text
rental-searching-app/
├── apps/
│   ├── web/            # Next.js frontend
│   ├── api/            # FastAPI backend
│   └── ai/             # AI/RAG utilities and workflow layer
├── packages/
│   └── shared/         # future shared config/types
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── package.json
└── package-lock.json
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

This starts the frontend and backend together in a development-friendly monorepo flow.

### 3) Run API tests

```powershell
cd "c:\rental-searching-app"
python -m pytest -q apps/api/tests
```

### Useful URLs

- http://localhost:3000
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/public-rentals?city=Danville&state=CA&limit=5
- http://127.0.0.1:8000/api/live-feed

## Production deployment readiness

This repo is aligned for a real deployment workflow:

- separate app boundaries for web, API, and AI
- environment-driven configuration via `.env` files
- Docker support for backend and frontend containerization
- workspace-based setup for scalable multi-app development

### Frontend deployment

Use Vercel and set:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url
```

### Backend deployment

Use Render or Railway and expose the FastAPI app on port 8000.

```bash
cd apps/api
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

This makes the project solid as a portfolio-ready demo for AI product and full-stack roles.

## Real-data path

The current implementation uses a no-key public fallback:

- location lookup via OpenStreetMap Nominatim
- U.S. city/state matching for searchable markets
- public market feed for demo-ready results
- adapter-ready structure for future licensed data APIs

## Next milestones

- replace the public fallback with a real licensed rental data source
- add auth, saved homes, and user profiles
- stream AI responses in real time
- deploy frontend and backend to host environments
- refine the brand and product story for LinkedIn and interviews
