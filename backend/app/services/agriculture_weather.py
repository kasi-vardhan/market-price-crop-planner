from app.services.weather import (
    get_weather
)

from app.services.climate import (
    get_historical_rainfall
)


def get_agriculture_weather(
    location: str,
    season: str
):
    """
    Combine short-term weather with historical
    seasonal rainfall.
    """

    current_weather = get_weather(
        location
    )

    historical_climate = (
        get_historical_rainfall(
            location=location,
            season=season,
            years=3
        )
    )

    return {
        "current_weather": current_weather,
        "historical_climate": historical_climate
    }
