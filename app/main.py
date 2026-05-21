from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.dungeon import DEFAULT_ROOMS, MAX_ROOMS, MIN_ROOMS, generate_dungeon
from app.schemas import DungeonResponse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="AI Dungeon Map Explorer")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def add_basic_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:"
    )
    return response


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dungeon", response_model=DungeonResponse)
def api_dungeon(
    seed: int | None = Query(default=None),
    rooms: int = Query(default=DEFAULT_ROOMS, ge=MIN_ROOMS, le=MAX_ROOMS),
) -> DungeonResponse:
    return generate_dungeon(seed=seed, rooms=rooms)
