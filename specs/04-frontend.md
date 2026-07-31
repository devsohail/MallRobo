# Frontend Specification

## Component Tree
```
App
├── StoreSelector       — dropdown to pick a store
├── ProductList          — products for selected store, "Add to Cart" buttons
├── Cart                 — cart items, quantities, remove button, total price
├── GridCanvas           — visual grid with obstacles, path, numbered cells
└── RouteSummary         — total price, total delivery time, exact/heuristic badge
```

## Behaviors
- StoreSelector: fetches stores on mount, selecting a store fetches its products
- ProductList: displays product name, price, location; "Add" button adds to cart state
- Cart: shows items with quantity controls and remove; cart lives in React state (no backend)
- GridCanvas: renders the grid; obstacles are dark, path cells are light, robot start is marked,
  product locations are labeled, route path is drawn with numbered steps
- RouteSummary: shows total price (sum of cart), delivery seconds, whether solution is exact

## Route Computation
- On every cart change, debounce 300ms then POST /api/route with product_ids
- Display loading state during computation
- Handle errors (409 unreachable, network errors) with user-visible messages

## Styling
- Tailwind CSS utility classes
- Responsive layout is a stretch goal; desktop-first is fine
- Grid cells rendered as fixed-size squares in a CSS grid or canvas

## QA requirements
- Every component must have tests in `frontend/src/__tests__/` using vitest + React Testing Library
- Test matrix:
  - StoreSelector: loading state, renders stores from API, selection callback, error state
  - ProductList: no-store placeholder, loading, renders products, Add button callback, error, empty state
  - Cart: empty message, renders items with price, quantity display, +/- callbacks, remove callback, total price calculation
  - RouteSummary: null state (renders nothing), loading, error, price, delivery time, exact/heuristic badge, stop count
  - GridCanvas: loading state, cell rendering, start marker (S), visit order numbers, product markers (P), legend
  - API client: all functions call correct URLs, error handling (ApiError class)
- Use `src/test/helpers.ts` factory functions for test data
- Mock API calls with `vi.mock('../api/client')`
- Full suite must pass: `cd frontend && npx vitest run --reporter=verbose`

## Security requirements
- No `dangerouslySetInnerHTML` — all user-visible text rendered as React text nodes
- No `eval()`, `Function()`, or `innerHTML` usage
- Product names, store names, and all data from the API must be rendered as text (prevent stored XSS)
- Only `VITE_API_URL` is allowed as a `VITE_*` environment variable — no secrets in frontend env
- `fetch()` calls must use proper URL construction from `VITE_API_URL` constant, not user-controlled input
- No sensitive data (tokens, passwords, internal URLs) in client-side code or browser console logs
