# API Specification

Base path: `/api`

## Endpoints

### GET /api/stores
Response 200:
```json
[{ "id": "uuid", "name": "string" }]
```

### GET /api/stores/{store_id}/products
Response 200:
```json
[{ "id": "uuid", "name": "string", "price": 10.99, "x": 3, "y": 5, "store_id": "uuid" }]
```
Response 404: `{ "detail": "Store not found" }`

### POST /api/route
Request:
```json
{ "product_ids": ["uuid", ...] }
```
- product_ids: list[UUID], max length 50
- Empty list returns zero-length route from start

Response 200:
```json
{
  "visit_order": [{"x": 1, "y": 2}, ...],
  "cells": [{"x": 0, "y": 0}, ...],
  "total_seconds": 42,
  "total_price": 59.97,
  "exact": true
}
```
Response 409: `{ "detail": "Unreachable products", "product_ids": ["uuid", ...] }`
Response 404: `{ "detail": "Products not found", "product_ids": ["uuid", ...] }`
Response 422: Pydantic validation error (malformed body, too many items)

### GET /api/grid
Response 200:
```json
{
  "width": 14,
  "height": 9,
  "cells": [{ "x": 0, "y": 0, "path": true, "robot_start": false }, ...]
}
```

## Error Format
All errors return `{ "detail": "string", ... }` with appropriate HTTP status codes.
Error responses must NEVER expose: stack traces, internal file paths, database details, or environment variables.

## CORS
- Development: allow localhost origins
- Production: restrict to Vercel deployment domain (never `*`)
- Allowed methods: GET, POST only

## QA requirements
- Every endpoint must have tests for: correct schema, every documented error code, malformed input
- API tests live in `backend/tests/test_api.py` using the `client` fixture from `conftest.py`
- Test matrix:
  - GET /api/stores: 200 schema
  - GET /api/stores/{id}/products: 200 schema, 404 missing store, 422 invalid UUID
  - GET /api/grid: 200 schema, verify robot_start exists, verify width/height
  - POST /api/route: 200 single/multiple products, path continuity, start/end, empty list, 404 missing products, 409 unreachable, 422 malformed/invalid/oversized (>50)
  - Duplicate product IDs handling

## Security requirements
- All path parameters validated as UUID — reject non-UUID with 422
- `product_ids` max length 50 enforced by Pydantic schema
- No SQL injection possible — all queries via SQLAlchemy ORM
- API must be resilient to:
  - SQL injection payloads in path params and request bodies
  - Path traversal attempts in store_id
  - Type confusion (wrong types in JSON body)
  - Oversized payloads and deeply nested JSON
  - Extra fields in request body (mass assignment) — must be ignored
- FastAPI docs (`/api/docs`) disabled when `ENV=production`
- Rate limiting recommended for `/api/route` (CPU-intensive endpoint)
