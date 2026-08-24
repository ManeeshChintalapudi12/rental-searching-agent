# RentWise AI

A portfolio-ready AI rental marketplace experience built with a three-layer architecture:

- Frontend: live search UI and experience layer
- API: FastAPI backend with real-time streaming and rental search endpoints
- AI: agentic workflow and market insight layer

This project is designed to stand out in AI, product, and software engineering portfolios because it combines user experience, backend orchestration, and AI reasoning in a single product story.

## Project structure

```text
rental-searching-app/
├── frontend/       # Next.js app for the product UI
├── api/            # FastAPI service and rental APIs
├── ai/             # AI orchestration, prompt workflows, and assistant logic
├── backend/        # working backend implementation
├── rental-app/     # legacy/demo app used during iteration
├── README.md
├── docker-compose.yml
└── .env.example
```

## Why this is portfolio-friendly

- real-time market feed using Server-Sent Events
- city-based search across U.S. locations
- no vendor key required for a usable demo experience
- production-style layered architecture for frontend, API, and AI
- strong story for LinkedIn and AI role interviews

## Run locally

### Frontend

```powershell
cd "c:\rental-searching-app\rental-app"
npx next dev -H 127.0.0.1 -p 3000
```

### API

```powershell
cd "c:\rental-searching-app\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Live endpoints

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/live-feed
- http://127.0.0.1:8000/api/public-rentals?city=Seattle&state=WA&limit=5

## AI layer

The AI folder is where prompt pipelines, agents, and structured reasoning logic can live for:

- intent parsing
- listing ranking
- deal-quality summaries
- conversational recommendations

## Portfolio positioning

This project demonstrates:

- full-stack product thinking
- backend API design
- real-time product UX
- AI integration strategy
- deployment-ready architecture and storytelling for AI-focused roles

## Next milestone ideas

- connect to a verified rental provider API with key support
- store search history in a database
- add auth and saved homes
- add streaming AI chat responses for candidate interviews and demos
