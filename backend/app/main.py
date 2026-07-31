from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import grid, route, stores

app = FastAPI(
    title="MallRobo API",
    description="Mall robot shopping cart route optimization",
    version="0.1.0",
    docs_url="/api/docs" if settings.env == "development" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(stores.router)
app.include_router(grid.router)
app.include_router(route.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
