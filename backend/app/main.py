import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.plan import router as plan_router
from app.routes.market import router as market_router

# Project root / frontend build directory
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST_DIR", str(BASE_DIR / "frontend" / "dist")))

raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
if raw_origins == "*":
    cors_kwargs = {
        "allow_origins": ["*"],
        "allow_credentials": False,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
else:
    allowed_origins = [
        origin.strip()
        for origin in (
            raw_origins
            or "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if origin.strip()
    ]
    cors_kwargs = {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["*"],
    }

app = FastAPI(
    title="Market Price and Crop Planning Helper",
    description="AI-powered agricultural decision support system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    **cors_kwargs,
)


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(plan_router)
app.include_router(market_router)

# Mount frontend assets directly for optimized static delivery
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
