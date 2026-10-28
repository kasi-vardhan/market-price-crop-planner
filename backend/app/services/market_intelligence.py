from app.services.market_price import (
    get_market_price
)

from app.services.historical_market_analysis import (
    analyze_historical_market
)


def analyze_market(crop: str):

    price_data = get_market_price(
        crop
    )

    if "error" in price_data:

        return {
            "status": "unavailable",
            "crop": crop,
            "price": price_data
        }

    historical_data = analyze_historical_market(
        crop=crop,
        market=price_data.get("market"),
        days=30
    )

    return {
        "status": "available",

        "crop": crop,

        "market": price_data.get(
            "market"
        ),

        "location": price_data.get(
            "location"
        ),

        "date": price_data.get(
            "date"
        ),

        "source": price_data.get(
            "source",
            "unknown"
        ),

        "current_price": {
            "min": price_data.get(
                "min_price"
            ),
            "modal": price_data.get(
                "modal_price"
            ),
            "max": price_data.get(
                "max_price"
            )
        },

        "historical": historical_data,
        "trend": historical_data.get("trend"),
        "outlook": historical_data.get("outlook")
    }
