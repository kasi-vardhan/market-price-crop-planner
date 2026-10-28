from app.services.weather import get_weather


def weather_tool(location: str):
    """
    Get weather information for a location.
    """

    return get_weather(location)
