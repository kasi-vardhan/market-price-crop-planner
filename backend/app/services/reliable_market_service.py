from app.services.real_market_repository import (
    get_real_market_prices
)

from app.services.market_cache import (
    get_cached_market_price
)


def validate_agmarknet_price(record: dict) -> bool:
    """
    Validate record according to AGMARKNET price validation rules:
    - Commodity, market, and date are recorded.
    - Prices are non-negative.
    - Minimum price <= modal price <= maximum price.
    """
    if not isinstance(record, dict):
        return False

    commodity = record.get("crop") or record.get("commodity")
    market = record.get("market")
    date = record.get("date") or record.get("arrival_date")

    if not commodity or not market or not date:
        return False

    modal_price = record.get("modal_price")
    if modal_price is None or modal_price < 0:
        return False

    min_price = record.get("min_price")
    max_price = record.get("max_price")

    if min_price is not None and min_price < 0:
        return False
    if max_price is not None and max_price < 0:
        return False

    if min_price is not None and max_price is not None:
        if not (min_price <= modal_price <= max_price):
            return False
    elif min_price is not None:
        if min_price > modal_price:
            return False
    elif max_price is not None:
        if modal_price > max_price:
            return False

    return True


def get_reliable_market_price(
    crop: str,
    state: str = "Andhra Pradesh"
):
    """
    Market-data strategy:

    1. Try live Government of India OGD data and validate with AGMARKNET rules.
    2. If unavailable, use validated cached data.
    3. If cache is unavailable or invalid, report unavailable.

    Never invent market prices.
    """

    live_response = get_real_market_prices(
        state=state,
        commodity=crop
    )

    if (
        live_response.get("status")
        == "live"
    ):

        records = live_response.get(
            "records",
            []
        )

        for record in records:
            if validate_agmarknet_price(record):
                return {
                    **record,
                    "current_price": record.get("current_price") or record.get("modal_price"),
                    "status": "live",
                    "source": (
                        "Government of India OGD"
                    )
                }

    # --------------------------------------------------
    # FALLBACK TO CACHE
    # --------------------------------------------------

    cached = get_cached_market_price(
        crop
    )

    if cached and "error" not in cached and validate_agmarknet_price(cached):

        return {
            **cached,
            "current_price": cached.get("current_price") or cached.get("modal_price"),
            "status": "cached"
        }

    # --------------------------------------------------
    # NO DATA
    # --------------------------------------------------

    return {
        "crop": crop,
        "status": "unavailable",
        "source": (
            "Government of India OGD"
        ),
        "error": (
            "No live or cached market data "
            "is available."
        )
    }
