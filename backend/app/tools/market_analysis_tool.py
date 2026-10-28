from app.services.reliable_market_service import (
    get_reliable_market_price
)

from app.services.historical_market_analysis import (
    analyze_market_windows
)


def market_analysis_tool(
    crop: str,
    state: str = "Andhra Pradesh"
):
    """
    Combine current mandi price with historical
    market analytics.
    """

    current = get_reliable_market_price(
        crop=crop,
        state=state
    )

    if current.get("status") == "unavailable":

        return {
            "crop": crop,
            "status": "unavailable",
            "current": current,
            "historical": {}
        }

    market = current.get(
        "market"
    )

    historical = analyze_market_windows(
        crop=crop,
        market=market
    )

    return {
        "crop": crop,
        "status": current.get(
            "status",
            "unknown"
        ),
        "source": current.get(
            "source",
            "unknown"
        ),
        "current": current,
        "historical": historical
    }
