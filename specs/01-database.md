# Database Schema

## Tables

### grid
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| x | INT | NOT NULL |
| y | INT | NOT NULL |
| path | BOOLEAN | NOT NULL, default false |
| robot_start | BOOLEAN | NOT NULL, default false |

- UNIQUE(x, y)
- CHECK: at most one row with robot_start=true (enforced via partial unique index)

### stores
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| name | VARCHAR(255) | NOT NULL, UNIQUE |

### products
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| name | VARCHAR(255) | NOT NULL |
| price | DECIMAL(10,2) | NOT NULL, CHECK > 0 |
| x | INT | NOT NULL |
| y | INT | NOT NULL |
| store_id | UUID | FK → stores.id, NOT NULL |

## Seed Data
- 14x9 grid matching the PDF example
- Multiple stores with products at various grid positions
- One robot_start cell

## QA requirements
- Test all models can be created and queried via in-memory SQLite (aiosqlite) using `tests/conftest.py` fixtures
- Verify UNIQUE constraints (grid x,y; store name) are enforced
- Verify FK constraints (product.store_id → stores.id) are enforced
- Verify CHECK constraint (price > 0) is enforced

## Security requirements
- All DB access through SQLAlchemy ORM with bound parameters — zero string-built SQL
- No raw `execute()` with f-strings or string concatenation
- DATABASE_URL comes from environment variable via pydantic-settings, never hardcoded
- Seed script must not contain production credentials
