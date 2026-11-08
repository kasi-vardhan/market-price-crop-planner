
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routes.plan import router as plan_router
from app.routes.market import router as market_router


# Project root / frontend build directory
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]


app = FastAPI(
    title="Market Price and Crop Planning Helper",
    description="AI-powered agricultural decision support system",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(plan_router)
app.include_router(market_router)


@app.get("/")
def home():
    index_file = FRONTEND_DIST / "index.html"

    if index_file.is_file():
        return FileResponse(index_file)

    return {
        "message": "Market Price and Crop Planning Helper API is running!",
        "frontend_status": "Build not found"
    }


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Do not turn unknown API requests into frontend pages.
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    if not FRONTEND_DIST.is_dir():
        raise HTTPException(status_code=404, detail="Frontend build not found")

    requested_file = (FRONTEND_DIST / full_path).resolve()
    frontend_root = FRONTEND_DIST.resolve()

    # Prevent access outside the frontend build directory.
    try:
        requested_file.relative_to(frontend_root)
    except ValueError:
        raise HTTPException(status_code=404, detail="File not found")

    if requested_file.is_file():
        return FileResponse(requested_file)

    # React SPA fallback for frontend routes.
    index_file = frontend_root / "index.html"

    if index_file.is_file():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend page not found")
