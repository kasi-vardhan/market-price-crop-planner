import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.plan import router as plan_router
from app.routes.market import router as market_router

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
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def home():

    return {
        "message": (
            "Market Price and Crop Planning "
            "Helper API is running!"
        )
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


app.include_router(
    plan_router
)

app.include_router(
    market_router
)