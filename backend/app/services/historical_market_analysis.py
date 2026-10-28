from datetime import datetime, timedelta
import statistics

from app.services.market_history_repository import (
    load_history
)

from app.utils.date_utils import (
    parse_market_date
)


def get_history_quality(
    observations: int,
    requested_days: int
):
    if observations >= 20:
        return "strong"

    if observations >= 7:
        return "moderate"

    if observations >= 2:
        return "weak"

    return "insufficient"


def analyze_historical_market(
    crop: str,
    market: str | None = None,
    days: int = 30
):
    """
    Analyze stored market observations for the
    requested time window.
    """

    history = load_history()

    crop = crop.lower().strip()

    cutoff_date = (
        datetime.now().date()
        - timedelta(days=days)
    )

    filtered = []

    for record in history:

        record_crop = str(
            record.get("crop", "")
        ).lower().strip()

        if record_crop != crop:
            continue

        if market:

            record_market = str(
                record.get("market", "")
            ).lower().strip()

            if (
                record_market
                != market.lower().strip()
            ):
                continue

        record_date = parse_market_date(
            record.get("date")
        )

        if record_date is None:
            continue

        if record_date < cutoff_date:
            continue

        modal_price = record.get(
            "modal_price"
        )

        if not isinstance(
            modal_price,
            (int, float)
        ):
            continue

        filtered.append({
            **record,
            "_parsed_date": record_date
        })

    if not filtered:

        return {
            "status": "unavailable",
            "crop": crop,
            "market": market,
            "window_days": days,
            "observations": 0,
            "data_quality": "insufficient",
            "message": (
                "No historical observations "
                "available for this period."
            )
        }

    filtered.sort(
        key=lambda item: item["_parsed_date"]
    )

    prices = [
        item["modal_price"]
        for item in filtered
    ]

    first_price = prices[0]
    latest_price = prices[-1]

    price_change = (
        latest_price - first_price
    )

    percentage_change = (
        price_change / first_price * 100
        if first_price != 0
        else 0
    )

    average_price = (
        sum(prices) / len(prices)
    )

    minimum_price = min(prices)
    maximum_price = max(prices)

    if len(prices) >= 2:

        standard_deviation = (
            statistics.pstdev(prices)
        )

        coefficient_of_variation = (
            standard_deviation
            / average_price
            if average_price != 0
            else 0
        )

    else:

        standard_deviation = 0
        coefficient_of_variation = 0

    if price_change > 0:
        trend = "rising"

    elif price_change < 0:
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

        "crop": crop,

        "market": market,

        "window_days": days,

        "observations": len(prices),

        "data_quality": get_history_quality(
            len(prices),
            days
        ),

        "prices": prices,

        "first_price": first_price,

        "latest_price": latest_price,

        "average_price": round(
            average_price,
            2
        ),

        "minimum_price": minimum_price,

        "maximum_price": maximum_price,

        "price_change": round(
            price_change,
            2
        ),

        "percentage_change": round(
            percentage_change,
            2
        ),

        "standard_deviation": round(
            standard_deviation,
            2
        ),

        "coefficient_of_variation": round(
            coefficient_of_variation,
            4
        ),

        "trend": trend,

        "outlook": outlook,

        "source": (
            "Stored Government of India "
            "OGD observations"
        )
    }


def analyze_market_windows(
    crop: str,
    market: str | None = None
):
    """
    Generate 7, 30 and 90 day analytics.
    """

    return {
        "7_day": analyze_historical_market(
            crop=crop,
            market=market,
            days=7
        ),

        "30_day": analyze_historical_market(
            crop=crop,
            market=market,
            days=30
        ),

        "90_day": analyze_historical_market(
            crop=crop,
            market=market,
            days=90
        )
    }
