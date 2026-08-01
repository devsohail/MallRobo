# MallRobo

Mall robot shopping cart system — pick products, compute optimal delivery routes.

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

## Setup

### Backend

```bash
cd backend
cp .env.example .env    # edit DATABASE_URL as needed
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env    # edit VITE_API_URL if backend is not localhost:8000
npm install
npm run dev
```

### Environment Variables

**Backend (.env):**
- `DATABASE_URL` — PostgreSQL connection string
- `CORS_ORIGINS` — comma-separated allowed origins
- `ENV` — `development` or `production`

**Frontend (.env):**
- `VITE_API_URL` — backend API base URL

## Testing

### Backend (pytest)

```bash
# Run all backend tests
cd backend && python -m pytest tests/ -v

# Run only pathfinding tests
cd backend && python -m pytest tests/test_pathfinding.py -v

# Run only API tests
cd backend && python -m pytest tests/test_api.py -v

# Run a specific test class
cd backend && python -m pytest tests/test_api.py::TestRoute -v

# Run a single test
cd backend && python -m pytest tests/test_api.py::TestRoute::test_single_product_route -v
```

### Frontend (vitest)

```bash
# Run all frontend tests
cd frontend && npx vitest run --reporter=verbose

# Run in watch mode (re-runs on file changes)
cd frontend && npx vitest

# Run a specific test file
cd frontend && npx vitest run src/__tests__/Cart.test.tsx

# Run tests matching a name pattern
cd frontend && npx vitest run -t "Cart"
```

### Lint, security & tests — all at once

```bash
./scripts/check.sh
```

Runs in sequence: ruff check, ruff format, bandit, pip-audit, **pytest**, eslint, tsc, npm audit, **vitest** — then prints a pass/fail summary.

### Test file structure

```
backend/tests/
├── conftest.py              # Fixtures: db_session, seeded_session, client
├── test_pathfinding.py      # BFS, Held-Karp, NN+2opt, solver (23 tests)
└── test_api.py              # Stores, grid, route endpoints (19 tests)

frontend/src/
├── test/
│   ├── setup.ts             # jest-dom matchers
│   └── helpers.ts           # Factory functions (makeStore, makeProduct, …)
└── __tests__/
    ├── Cart.test.tsx         # 7 tests
    ├── RouteSummary.test.tsx # 8 tests
    ├── StoreSelector.test.tsx# 4 tests
    ├── ProductList.test.tsx  # 6 tests
    ├── GridCanvas.test.tsx   # 7 tests
    └── client.test.ts        # 7 tests
```

## Docker Compose (local development)

Run the entire stack (PostgreSQL, backend, frontend) with a single command. Requires Docker and Docker Compose.

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API docs | http://localhost:8000/api/docs |
| PostgreSQL | localhost:5432 |

The backend container automatically runs migrations and seeds the database on startup. Source code is volume-mounted for hot-reload in both backend and frontend.

To stop and remove containers:

```bash
docker-compose down
```

To also remove the database volume:

```bash
docker-compose down -v
```

## Documentation

- [docs/TECHNICAL.md](docs/TECHNICAL.md) — Algorithm analysis
- [docs/DECISIONS.md](docs/DECISIONS.md) — Architectural decisions
- [CODE_AUDIT.md](CODE_AUDIT.md) — Security audit and architecture assessment
- [AI_REVIEW_LOG.md](AI_REVIEW_LOG.md) — Code review log and bug corrections