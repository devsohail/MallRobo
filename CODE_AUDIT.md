# Code Audit — MallRobo

**Date:** 2026-08-01
**Auditor:** Sohail Sajid
**Scope:** Full-stack security review and architecture assessment

---

## 1. Security Audit

### 1.1 Secrets & Environment Variables

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded passwords/tokens in source | PASS | All sensitive values via `pydantic-settings` (`app/config.py`) |
| `.env` files gitignored | PASS | Root `.gitignore` excludes `.env`, `.env.*`, allows `.env.example` |
| `.env.example` has safe placeholders only | PASS | `backend/.env.example`: localhost DB, `frontend/.env.example`: localhost API |
| No secrets in frontend env vars | PASS | Only `VITE_API_URL` (public endpoint) |
| No env vars logged or printed | PASS | `seed.py` prints "Database seeded successfully!" only; no config/env output |
| Docker Compose uses env vars, not secrets in code | PASS | `docker-compose.yml` uses local-only dev credentials, not committed `.env` |

### 1.2 Database Security

| Check | Status | Notes |
|-------|--------|-------|
| All DB access via SQLAlchemy ORM | PASS | No raw SQL anywhere in codebase |
| Parameterized queries only | PASS | All queries use SQLAlchemy expressions (`select`, `where`, `==`, `or_`) |
| No SQL string concatenation | PASS | — |
| DB credentials from env vars | PASS | `config.py:5` reads `database_url` from environment |

### 1.3 API Security

| Check | Status | Notes |
|-------|--------|-------|
| Pydantic-validated input on all endpoints | PASS | `RouteRequest`, `StoreResponse`, `ProductResponse`, `GridResponse` |
| `product_ids` capped at 50 | PASS | `RouteRequest.product_ids: list[uuid.UUID] = Field(..., max_length=50)` — prevents Held-Karp DoS (O(2^k)) |
| CORS restricted to specific origins | PASS | `cors_origins` from env var, parsed as comma-separated list; never `*` |
| FastAPI docs disabled in production | PASS | `docs_url="/api/docs" if settings.env == "development" else None` (`main.py:11`) |
| Structured error responses | PASS | 404 returns `{"detail": ..., "product_ids": [...]}`, 409 returns `{"detail": ..., "unreachable_points": [...]}` |
| No stack traces exposed to client | PASS | Custom exception handlers return JSON, no tracebacks |
| UUID-typed path/body parameters | PASS | Pydantic validates UUIDs before reaching service layer |

### 1.4 Frontend Security

| Check | Status | Notes |
|-------|--------|-------|
| No secrets in frontend code | PASS | Only `VITE_API_URL` used |
| No `dangerouslySetInnerHTML` | PASS | All rendering via React JSX |
| No user-generated HTML rendered | PASS | Product names rendered as text nodes |
| API errors handled gracefully | PASS | `ApiError` class with status/message, caught in `App.tsx` |

### 1.5 Infrastructure

| Check | Status | Notes |
|-------|--------|-------|
| `.dockerignore` excludes secrets | PASS | Both backend/frontend exclude `.env` |
| No secrets in Dockerfile | PASS | Environment injected at runtime |
| Health endpoint available | PASS | `GET /api/health` returns `{"status": "ok"}` |
| Volume mounts don't expose secrets | PASS | `docker-compose.yml` mounts source code only |

### 1.6 Findings

| # | Severity | Finding | Location | Recommendation |
|---|----------|---------|----------|----------------|
| 1 | LOW | `frontend/.env` exists on disk (gitignored but present) | `frontend/.env` | Confirm it contains only `VITE_API_URL`. No action needed if so. |
| 2 | INFO | `docker-compose.yml` uses default `postgres:postgres` credentials | `docker-compose.yml:5-6` | Acceptable for local dev. Production uses Railway-managed credentials. |
| 3 | INFO | `echo=True` in dev mode logs SQL queries to stdout | `database.py:7` | Only active when `ENV=development`. Disabled in production. |

---

## 2. Architecture Assessment

### 2.1 System Overview

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Frontend   │────▶│   Backend    │────▶│ PostgreSQL │
│  React + TS  │     │   FastAPI    │     │            │
│  Vite + TW   │     │  Python 3.12 │     │            │
└─────────────┘     └──────────────┘     └────────────┘
   Vercel              Railway              Railway
   Port 5173           Port 8000            Port 5432
```

### 2.2 Backend Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # pydantic-settings (env vars)
│   ├── database.py          # SQLAlchemy async engine + session
│   ├── models.py            # ORM models (GridCell, Store, Product)
│   ├── seed.py              # Database seeding (14x9 grid, 5 stores, 15 products)
│   ├── routers/
│   │   ├── stores.py        # GET /api/stores, GET /api/stores/{id}/products
│   │   ├── grid.py          # GET /api/grid
│   │   └── route.py         # POST /api/route
│   ├── schemas/             # Pydantic request/response models
│   ├── services/
│   │   └── route_service.py # Business logic: load grid, fetch products, compute route
│   └── pathfinding/         # Pure Python, no framework imports
│       ├── bfs.py           # BFS shortest path, distance matrix
│       ├── tsp.py           # Held-Karp (exact) + NN+2-opt (heuristic)
│       └── solver.py        # Orchestrator: BFS → TSP → path reconstruction
```

**Key design decisions:**
- Pathfinding module is **pure Python** — no SQLAlchemy, FastAPI, or framework imports. Fully unit-testable in isolation.
- Two-phase route computation: BFS for grid distances, TSP for visit ordering.
- Adaptive algorithm selection: exact (Held-Karp) for ≤12 waypoints, heuristic (NN+2-opt) for >12.
- Async throughout: asyncpg driver, async SQLAlchemy sessions, async FastAPI endpoints.

### 2.3 Frontend Architecture

```
frontend/src/
├── App.tsx                  # Main layout, state management, route computation
├── api/client.ts            # API client (fetch wrapper, error handling)
├── types/index.ts           # TypeScript interfaces
├── components/
│   ├── StoreSelector.tsx    # Store dropdown
│   ├── ProductList.tsx      # Product cards with Add button
│   ├── Cart.tsx             # Cart with quantity controls
│   ├── GridCanvas.tsx       # Grid visualization with animation
│   └── RouteSummary.tsx     # Route stat cards (price, time, stops)
```

**Key design decisions:**
- 3-panel layout: left (store/products), center (grid + stats), right (cart)
- Route computed via debounced API call (300ms) on cart changes
- Grid path animation: sequential cell highlighting at 50ms/step with cleanup on route change
- All state in `App.tsx` — no external state management library (appropriate for this scale)

### 2.4 Pathfinding Algorithm Analysis

| Phase | Algorithm | Complexity | When Used |
|-------|-----------|------------|-----------|
| Grid distances | BFS (all-pairs) | O(n * \|grid\|) | Always |
| Visit ordering | Held-Karp DP | O(2^k * k²) | ≤12 waypoints |
| Visit ordering | NN + 2-opt | O(k² * iterations) | >12 waypoints |
| Path reconstruction | Parent backtracking | O(path length) | Always |

**Why BFS over A\*:** Grid is unweighted. BFS is optimal with O(1) queue operations. A\* adds priority queue overhead (O(log n)) and heuristic computation for zero benefit. Additionally, BFS from one source yields all-pairs distances in a single pass.

**DoS protection:** `product_ids` capped at 50 in Pydantic schema. With Held-Karp threshold at 12, worst case is NN+2-opt for 13-50 waypoints (polynomial, not exponential).

### 2.5 Data Flow

```
User adds product to cart
  → App.tsx debounces (300ms)
    → POST /api/route { product_ids: [...] }
      → Pydantic validates (UUIDs, max 50)
        → route_service: load grid + fetch products from DB
          → pathfinding.solver: BFS distance matrix → TSP → path reconstruction
        → Return RouteResponse { visit_order, cells, total_seconds, total_price, exact }
      → GridCanvas animates route cells sequentially
      → RouteSummary displays stat cards
```

### 2.6 Deployment

| Component | Platform | Build | Config |
|-----------|----------|-------|--------|
| Frontend | Vercel | `npm run build` (Vite) | `VITE_API_URL` env var |
| Backend | Railway | Dockerfile (Python 3.12-slim) | `DATABASE_URL`, `CORS_ORIGINS`, `ENV` |
| Database | Railway | Managed PostgreSQL 16 | Auto-provisioned |
| Local dev | Docker Compose | All 3 services | `docker-compose.yml` |

### 2.7 Test Coverage

| Suite | Tests | Framework | Target |
|-------|-------|-----------|--------|
| Backend API | 15 | pytest + httpx | Endpoints, error cases |
| Backend pathfinding | 27 | pytest | BFS, TSP, solver, edge cases |
| Frontend components | 39 | vitest + testing-library | All components, animation, API client |

---

## 3. Summary

**Security posture:** Solid. No hardcoded secrets, all inputs validated, CORS restricted, SQL injection not possible via ORM, DoS mitigated via product cap.

**Architecture:** Clean separation of concerns. Pathfinding is framework-independent. Frontend is straightforward React without unnecessary abstraction.

**Known issues addressed:**
- asyncpg UUID `IN` clause binding (fixed with `OR` conditions)
- Docker Compose build context mismatch (fixed with repo-root context)
- `entrypoint.sh` permission issue with volume mounts (fixed with `chmod +x`)
