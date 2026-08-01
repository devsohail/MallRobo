# Technical Documentation

## Assumptions

### From the assessment specification

- The mall is a single-floor rectangular area mapped as a coordinate grid
- Only one robot operates at a time — no moving obstacles
- Product pickup time is negligible (0 seconds)
- Robot speed is constant: 1 second per cell movement
- Movement is 4-directional (horizontal/vertical only, no diagonals)
- Grid configuration and product locations are static during order processing
- Exactly one cell is designated as `robot_start` (enforced at the database layer)

### Implementation assumptions

- **Exact vs. heuristic threshold:** carts with <= 12 unique pickup locations get an exact optimal tour (Held-Karp); larger carts use NN + 2-opt, typically within 5-15% of optimal. The API response flags which was used (`exact: true/false`).
- **Cart is client-side state:** no cart persistence, sessions, or user accounts — the kiosk scenario doesn't require them. Route computation is stateless per request.
- **Product coordinates are trusted at seed time** to lie on accessible grid cells; if not, the route endpoint returns HTTP 409 rather than crashing.
- **Quantity does not affect routing:** ordering 3 units of the same product requires one visit to its location; quantity only affects total price.
- **`product_ids` per request is capped** to bound Held-Karp/matrix computation and prevent algorithmic DoS.
- **Grid size is kiosk-scale** (tens x tens of cells); the grid is loaded from the DB per request and BFS is O(R*C), so no spatial indexing is needed at this scale.
- **Estimated delivery time = path length in seconds** (1 sec/cell), since pickup time is zero by assumption.

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
