# 🛒 CartQuest — Multi-Agent Shopping List Optimizer

**DiamondHacks 2026 — Enchanted Commerce Track + Best Use of Browser Use**

CartQuest takes your grocery list and zip code, dispatches parallel Browser Use agents to real store websites (Walmart, Target, Vons/Albertsons), and finds the cheapest way to buy everything — including whether it's worth splitting across multiple stores.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   React UI  │────▶│  FastAPI Server  │────▶│  Orchestrator       │
│  (Vite)     │◀────│  /api/optimize   │◀────│                     │
└─────────────┘     └──────────────────┘     │  ┌───────────────┐  │
                                             │  │ Ralph's Agent │  │
                                             │  └───────────────┘  │
                                             │  ┌───────────────┐  │
                                             │  │ Target Agent  │  │
                                             │  └───────────────┘  │
                                             │  ┌───────────────┐  │
                                             │  │ TJ's Agent    │  │
                                             │  └───────────────┘  │
                                             └─────────────────────┘
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Run the server
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment Variables

```
OPENAI_API_KEY=sk-...          # or use ANTHROPIC_API_KEY / BROWSER_USE_API_KEY
BROWSER_USE_API_KEY=...        # optional: for Browser Use Cloud
```

## How It Works

1. User enters a grocery list + zip code (defaults to 92092 / UCSD area)
2. FastAPI server receives the request and spawns the Orchestrator
3. Orchestrator creates one Browser Use Agent per store, each with its own Browser instance
4. Agents run **in parallel** via `asyncio.gather()` — each navigates to a real store website, sets the location, searches for each item, and extracts prices
5. Orchestrator collects all results, normalizes item names, and runs the optimizer
6. Optimizer calculates: single-store totals, best per-item picks, and whether a multi-store split saves enough to justify extra trips (configurable trip-cost threshold)
7. Results stream back to the frontend as Server-Sent Events (SSE) so users can watch agent progress in real time

## Project Structure

```
grocery-optimizer/
├── backend/
│   ├── main.py              # FastAPI app + SSE endpoint
│   ├── orchestrator.py      # Spawns & coordinates parallel agents
│   ├── agents/
│   │   ├── base.py          # Base store agent config
│   │   ├── walmart.py       # Walmart-specific agent task
│   │   ├── target.py        # Target-specific agent task
│   │   └── vons.py          # Vons/Albertsons agent task
│   ├── optimizer.py         # Price comparison + multi-store optimization
│   ├── models.py            # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/
│       │   ├── GroceryInput.jsx
│       │   ├── AgentStatus.jsx
│       │   └── ResultsDashboard.jsx
│       └── styles/
│           └── global.css
└── README.md
```

## Demo Tips

- Pre-load a grocery list: `eggs, chicken breast, oat milk, rice, bananas, greek yogurt, bread, spinach`
- Use zip `92092` (UCSD / La Jolla)
- Show the agent browser windows side-by-side during the demo
- Have a backup set of cached results in case of network issues

## Team: Solo

Built at ACM DiamondHacks 2026, UC San Diego
