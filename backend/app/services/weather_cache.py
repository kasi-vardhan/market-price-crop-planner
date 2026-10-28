import json
from pathlib import Path


CACHE_PATH = Path(
    "../data/weather_cache/weather.json"
) if Path("../data/weather_cache/weather.json").exists() else Path(
    "data/weather_cache/weather.json"
)


def get_cached_weather(
    location: str
):

    if not CACHE_PATH.exists():

        return {
            "error":
            "Weather cache not found."
        }

    try:

        with open(
            CACHE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        return {
            "error":
            f"Could not read weather cache: {error}"
        }

    location = location.lower().strip()

    if location not in data:

        return {
            "error":
            f"No cached weather for {location}"
        }

    return {
        "location": location,
        **data[location],
        "rainfall": data[location].get("rainfall", data[location].get("daily_rainfall", 0.0)),
        "status": "cached"
    }
