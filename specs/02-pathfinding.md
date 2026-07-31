# Pathfinding Contract

## Input
- grid: set of accessible cells (path=1) within bounds; one start cell (robot_start=1)
- waypoints: deduplicated set of product (x, y) locations

## Algorithm — REQUIRED approach
1. Deduplicate waypoints; drop none silently — if any waypoint is not an accessible
   cell or unreachable from start, raise UnreachableProductError (maps to HTTP 409
   listing the offending product ids).
2. Multi-source distance matrix: run BFS from start and from each waypoint.
   D[i][j] = shortest path length; also retain parent maps for path reconstruction.
3. Order:
   - if k <= 12: Held-Karp over D, cycle constraint (return to start). Exact.
   - if k > 12: nearest-neighbor seed + 2-opt until no improving swap. Heuristic.
4. Reconstruct full cell sequence by concatenating BFS paths between consecutive
   ordered waypoints. total_seconds = len(cells) - 1.

## Output
RouteResult { visit_order: list[Point], cells: list[Point], total_seconds: int, exact: bool }

## Invariants (QA enforces)
- cells[0] == cells[-1] == start
- every consecutive pair is 4-adjacent and both accessible
- every waypoint appears in cells
- for k <= 6, total_seconds equals brute-force optimum
- empty cart -> cells=[start], total_seconds=0

## Complexity documentation duty
Whoever edits this module updates the Big-O table in docs/TECHNICAL.md in the same PR.

## QA requirements
- Every invariant listed above must have a corresponding test in `tests/test_pathfinding.py`
- Pathfinding test matrix (see specs/06-testing.md) is mandatory for every change to this module
- Performance gate: k=12 must complete in < 2 seconds — tested in CI
- Any new algorithm variant must be verified against brute-force for k <= 6
- Full test suite must pass after any change: `cd backend && python -m pytest tests/ -v`

## Security requirements
- Pure Python only — no framework imports (FastAPI, SQLAlchemy, etc.)
- No file I/O, network calls, or subprocess usage in pathfinding code
- `product_ids` capped at 50 at the API layer to prevent algorithmic DoS (k=50 with Held-Karp would be O(2^50) — this is why the heuristic fallback exists)
- Unreachable product detection must not hang — BFS terminates in O(V+E)
