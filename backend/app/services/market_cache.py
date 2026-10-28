import json
from pathlib import Path


CACHE_PATH = Path(
    "../data/market_cache/market_prices.json"
) if Path("../data/market_cache/market_prices.json").exists() else Path(
    "data/market_cache/market_prices.json"
)


def load_market_cache():

    if not CACHE_PATH.exists():

        return {
            "error": "Market cache not found."
        }

    try:

        with open(
            CACHE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (OSError, json.JSONDecodeError) as error:

        return {
            "error": f"Could not read market cache: {error}"
        }


def get_cached_market_price(
    crop: str
):

    cache = load_market_cache()

    if "error" in cache:
        return cache

    crop = crop.lower().strip()

    for record in cache.get(
        "records",
        []
    ):

        if record["crop"].lower() == crop:

            return {
                **record,
                "source": cache.get(
                    "source",
                    "cache"
                ),
                "cached_at": cache.get(
                    "updated_at"
                )
            }

    return {
        "error":
        f"No cached market data available for {crop}"
    }
