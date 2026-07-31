# Technical Documentation

## Algorithm Design

### Problem Decomposition

The robot route optimization breaks into two subproblems:

1. **Shortest path between grid points** — BFS on an unweighted obstacle grid
2. **Optimal visiting order (TSP)** — Held-Karp DP or NN+2-opt heuristic

### Complexity Analysis

| Step | Time Complexity | Space Complexity |
|------|----------------|-----------------|
| BFS from each of k+1 waypoints | O(k * R*C) | O(R*C) |
| Held-Karp (k <= 12) | O(2^k * k^2) | O(2^k * k) |
| NN + 2-opt (k > 12) | O(k^2 * iterations) | O(k^2) |
| Path reconstruction | O(total_path_length) | O(total_path_length) |

Where:
- k = number of unique product pickup locations
- R, C = grid dimensions (rows, columns)

### Algorithm Details

**BFS (Breadth-First Search):**
- Optimal for unweighted grids — every edge has cost 1
- A* provides no benefit here since we need all-pairs distances anyway
- Each BFS runs in O(R*C), producing both distance and parent maps for path reconstruction

**Held-Karp (k <= 12):**
- Dynamic programming approach using bitmask to track visited nodes
- Guarantees exact optimal tour
- Practical limit: k=12 gives 2^12 * 144 = ~590K states — fast enough

**Nearest-Neighbor + 2-opt (k > 12):**
- Greedy construction: always visit the nearest unvisited node
- 2-opt local search: try reversing every sub-segment, accept improvements
- Typically within 5-15% of optimal

### Edge Cases

| Case | Handling |
|------|---------|
| Empty cart | Return start position only, total_seconds=0 |
| Unreachable product | UnreachableProductError -> HTTP 409 |
| Product on obstacle | UnreachableProductError -> HTTP 409 |
| Duplicate locations | Deduplicated, visited once |
| No robot_start defined | ValueError at service layer |
| Start cell blocked | UnreachableProductError |

## Architecture

See [DECISIONS.md](DECISIONS.md) for architectural decision records.

### Backend Structure
```
backend/app/
  config.py          — pydantic-settings, loads from .env
  database.py        — async SQLAlchemy engine + session
  models.py          — GridCell, Store, Product (UUID PKs)
  main.py            — FastAPI app, CORS, router registration
  seed.py            — seed script with 14x9 grid + sample data
  schemas/           — Pydantic v2 request/response models
  routers/           — API endpoint handlers
  services/          — business logic (route computation)
  pathfinding/       — pure Python algorithms (BFS, TSP, solver)
```

### Frontend Structure
```
frontend/src/
  api/client.ts      — API client functions, no hardcoded URLs
  types/index.ts     — TypeScript interfaces
  components/
    StoreSelector    — store dropdown
    ProductList      — product cards with "Add" buttons
    Cart             — cart items with quantity controls
    GridCanvas       — grid visualization with route overlay
    RouteSummary     — price, time, exact/heuristic badge
```
