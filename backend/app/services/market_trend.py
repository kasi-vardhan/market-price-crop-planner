HISTORICAL_PRICES = {
    "tomato": [
        22, 23, 21, 24, 25, 26, 25
    ],
    "chilli": [
        105, 108, 110, 115, 118, 120, 120
    ],
    "groundnut": [
        65, 66, 64, 67, 69, 70, 70
    ],
    "paddy": [
        23, 23, 24, 24, 25, 25, 25
    ]
}


def get_market_trend(crop: str):

    crop = crop.lower().strip()

    if crop not in HISTORICAL_PRICES:

        return {
            "status": "unavailable",
            "error": (
                f"No historical data available "
                f"for {crop}"
            )
        }

    prices = HISTORICAL_PRICES[crop]

    if len(prices) < 2:

        return {
            "status": "unavailable",
            "error": (
                "Insufficient historical data."
            )
        }

    first_price = prices[0]

    latest_price = prices[-1]

    change = latest_price - first_price

    percentage_change = (
        (change / first_price) * 100
        if first_price
        else 0
    )

    if change > 0:
        trend = "rising"

    elif change < 0:
        trend = "falling"

    else:
        trend = "stable"

    if percentage_change >= 10:
        outlook = "positive"

    elif percentage_change <= -10:
        outlook = "negative"

    else:
        outlook = "stable"

    return {
        "status": "available",
        "source": "demo-historical-data",
        "crop": crop,
        "prices": prices,
        "first_price": first_price,
        "latest_price": latest_price,
        "price_change": round(
            change,
            2
        ),
        "percentage_change": round(
            percentage_change,
            2
        ),
        "trend": trend,
        "outlook": outlook
    }