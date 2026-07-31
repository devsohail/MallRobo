# Architectural Decision Records

## ADR-1: FastAPI for Backend
**Decision:** Use FastAPI with Python 3.12
**Rationale:** Async support, automatic OpenAPI docs, Pydantic-native validation, strong typing. Assessment requires Python backend.

## ADR-2: BFS + Held-Karp for Pathfinding
**Decision:** BFS for shortest paths on unweighted grid, Held-Karp DP for TSP when k <= 12, NN + 2-opt heuristic for k > 12.
**Rationale:** BFS is optimal for unweighted grids (A* adds no benefit). Held-Karp gives exact optimum in O(2^k * k^2) which is tractable for k <= 12. Heuristic fallback ensures the system doesn't choke on larger inputs.

## ADR-3: Stateless Route Computation
**Decision:** Cart lives in React state. Route computation is a stateless POST endpoint.
**Rationale:** No cart table, no sessions, no cleanup. Cart is ephemeral by nature (kiosk use case). Simpler, safer, sufficient for the requirements.

## ADR-4: UUID Primary Keys
**Decision:** Use UUID v4 for all primary keys instead of auto-incrementing integers.
**Rationale:** Avoids enumeration attacks, safe for distributed systems, no sequential ID leakage.

## ADR-5: Environment-Driven Configuration
**Decision:** All URLs, keys, and configuration values loaded from environment variables via .env files.
**Rationale:** No hardcoded values in source code. Supports multiple deployment environments (dev, staging, production) without code changes.
