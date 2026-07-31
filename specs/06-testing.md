# Testing Specification

## Mandatory workflow — every feature

This workflow is compulsory. No feature is considered done until all steps pass.

1. **feature-dev** writes tests alongside implementation code
2. **qa-engineer** reviews and writes additional edge-case tests
3. **qa-engineer** runs the new tests, then the full sanity suite
4. **If a bug is found**: write a failing test, log in AI_REVIEW_LOG.md, report for fix
5. **security-auditor** runs security checks (see Security Testing below)
6. **All checks must pass**: `./scripts/check.sh` exits 0

## Test infrastructure

### Backend
- Framework: pytest with pytest-asyncio
- Config: `backend/pyproject.toml` → `[tool.pytest.ini_options]`
- Fixtures: `backend/tests/conftest.py` provides:
  - `db_session` — clean in-memory SQLite via aiosqlite
  - `seeded_session` — pre-populated with 5x5 grid, 1 store, 3 products
  - `client` — async HTTPX client wired to FastAPI with DB override
- Run: `cd backend && python -m pytest tests/ -v`

### Frontend
- Framework: vitest + React Testing Library + jest-dom
- Config: `frontend/vite.config.ts` → `test` section
- Helpers: `frontend/src/test/helpers.ts` — factory functions (`makeStore`, `makeProduct`, `makeCartItem`, `makeGrid`, `makeRoute`)
- Setup: `frontend/src/test/setup.ts` — jest-dom matchers
- Mock API: `vi.mock('../api/client')`
- Run: `cd frontend && npx vitest run --reporter=verbose`

## Backend — pytest

### Pathfinding test matrix (`tests/test_pathfinding.py`)
| Test Case | Expected |
|-----------|----------|
| Same start and goal | distance=0, path=[start] |
| Single product, straight line | Optimal path length |
| Product adjacent to start | total_seconds = 2 (go + return) |
| Path forced around obstacles | Longer path, still optimal |
| Multiple products, order matters (k <= 6) | Matches brute-force optimum |
| Unreachable product (obstacle-locked) | UnreachableProductError |
| Empty cart | cells=[start], total_seconds=0 |
| Duplicate product locations | Visited once, same as single |
| k=12 completes < 2s | Performance gate |
| Product on blocked cell | UnreachableProductError |
| Path continuity | Every consecutive pair is 4-adjacent |
| Returns to start | cells[0] == cells[-1] == start |
| All waypoints visited | Every waypoint appears in cells |
| Large grid single product | Valid path on 14x9 grid |
| NN+2opt quality | Within 2x of optimal for small cases |

### API test matrix (`tests/test_api.py`)
| Endpoint | Test Case | Expected |
|----------|-----------|----------|
| GET /api/health | Health check | 200, `{"status": "ok"}` |
| GET /api/stores | Schema validation | 200, list with id + name |
| GET /api/stores/{id}/products | Valid store | 200, list with all product fields |
| GET /api/stores/{id}/products | Non-existent store | 404 |
| GET /api/stores/{id}/products | Invalid UUID | 422 |
| GET /api/grid | Schema validation | 200, width + height + cells |
| GET /api/grid | Required fields | Every cell has x, y, path, robot_start |
| GET /api/grid | Robot start | Exactly one cell with robot_start=true |
| POST /api/route | Single product | 200, correct price, exact=true |
| POST /api/route | Multiple products | 200, correct total price, all visited |
| POST /api/route | Path continuity | Every consecutive pair is 4-adjacent |
| POST /api/route | Start/end position | cells[0] == cells[-1] == start |
| POST /api/route | Empty product_ids | 200, total_seconds=0 |
| POST /api/route | Non-existent product | 404 with product_ids |
| POST /api/route | Malformed body | 422 |
| POST /api/route | Invalid UUID in body | 422 |
| POST /api/route | Missing body | 422 |
| POST /api/route | >50 product_ids | 422 |
| POST /api/route | Duplicate product IDs | 200, deduplicated |

## Frontend — vitest + React Testing Library

### Component test matrix (`src/__tests__/`)
| Component | Test Case |
|-----------|-----------|
| StoreSelector | Loading state, renders stores from API, selection callback, error state |
| ProductList | No-store placeholder, loading, renders products, Add callback, error, empty state |
| Cart | Empty message, renders items with price, quantity display, +/- callbacks, remove callback, total price |
| RouteSummary | Null (renders nothing), loading, error, price, delivery time, exact/heuristic badge, stop count, error priority over loading |
| GridCanvas | Loading, cell count, start marker (S), visit order numbers, product markers (P), legend |
| API client | All 4 functions call correct URLs with correct params, ApiError class, error handling for 409/500 |

## Performance verification
Time the route computation at k = 2, 6, 10, 12 and verify growth is consistent
with documented O(2^k * k^2) complexity. Flag if empirical growth contradicts documentation.

## Security testing

The security-auditor must run these checks after every feature and before deployment:

### Hardcoded values scan
- Grep codebase (excluding node_modules) for: `password=`, `secret=`, `token=`, `api_key=`, connection strings (`postgresql://`, `postgres://`), private keys (`-----BEGIN`)
- Zero tolerance: any hardcoded secret is a blocker

### Environment variable exposure
- `.env` gitignored, `.env.example` has only safe placeholder values
- No `VITE_SECRET_*`, `VITE_PASSWORD_*`, `VITE_TOKEN_*` in frontend
- No env vars logged/printed in code (`print(.*settings`, `console.log.*env`)
- Error responses do not expose stack traces or config values

### API attack surface
- SQL injection payloads in path params and request bodies → must return 422, not crash
- Path traversal in store_id → must return 422
- Type confusion in JSON body (string, null, bool, nested) → must return 422
- Oversized payloads and >50 product_ids → must return 422
- Extra fields in request body → must be ignored (no mass assignment)
- CORS not `*` in production, allowed methods = GET + POST only
- FastAPI docs disabled when ENV=production

### Dependency scanning
- `pip-audit` — zero high/critical CVEs
- `npm audit --audit-level=moderate` — zero moderate+ vulnerabilities
- `bandit -r app/ -q` — zero findings

## Full check command
```bash
./scripts/check.sh
```
Runs: ruff check, ruff format, bandit, pip-audit, pytest, eslint, tsc, npm audit, vitest.
All must pass (exit 0) before any commit or deployment.
