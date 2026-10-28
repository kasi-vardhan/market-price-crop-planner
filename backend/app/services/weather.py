import requests

from app.services.location_data import get_coordinates
from app.services.weather_cache import get_cached_weather


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(location: str):

    coordinates = get_coordinates(location)

    if "error" in coordinates:
        return coordinates

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": "temperature_2m,precipitation,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 1,
        "timezone": "auto"
    }

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        cached = get_cached_weather(location)
        if "error" not in cached:
            return cached

        return {
            "error": f"Weather API request failed: {error}"
        }

    except ValueError:
        cached = get_cached_weather(location)
        if "error" not in cached:
            return cached

        return {
            "error": "Weather API returned invalid JSON."
        }

    current = data.get("current", {})
    daily = data.get("daily", {})

    temperature = current.get("temperature_2m")
    precipitation = current.get("precipitation")
    weather_code = current.get("weather_code")

    max_temperature = None
    min_temperature = None
    daily_rainfall = None

    if daily.get("temperature_2m_max"):
        max_temperature = daily["temperature_2m_max"][0]

    if daily.get("temperature_2m_min"):
        min_temperature = daily["temperature_2m_min"][0]

    if daily.get("precipitation_sum"):
        daily_rainfall = daily["precipitation_sum"][0]

    return {
        "location": location,
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "temperature": temperature,
        "precipitation": precipitation,
        "temperature_max": max_temperature,
        "temperature_min": min_temperature,
        "daily_rainfall": daily_rainfall,
        "rainfall": daily_rainfall if daily_rainfall is not None else (precipitation or 0.0),
        "weather_code": weather_code,
        "source": "Open-Meteo",
        "status": "live"
    }
