from fastapi import APIRouter

from app.services.market_history_collector import (
    collect_market_history
)

from app.services.historical_market_analysis import (
    analyze_market_windows
)


router = APIRouter(
    prefix="/api/market",
    tags=["Market"]
)


@router.post("/collect")
def collect_market_data():

    return collect_market_history(
        state="Andhra Pradesh"
    )


@router.get("/analytics/{crop}")
def market_analytics(
    crop: str,
    market: str | None = None
):

    return {
        "crop": crop,
        "market": market,
        "analytics": analyze_market_windows(
            crop=crop,
            market=market
        )
    }
