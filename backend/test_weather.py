from app.services.weather import get_weather


result = get_weather(
    "markapur"
)


print("\n==============================")
print("REAL WEATHER DATA")
print("==============================")


if "error" in result:

    print(
        "ERROR:",
        result["error"]
    )

else:

    print(
        "Location:",
        result["location"]
    )

    print(
        "Temperature:",
        result["temperature"],
        "°C"
    )

    print(
        "Today's Rainfall:",
        result["daily_rainfall"],
        "mm"
    )

    print(
        "Maximum Temperature:",
        result["temperature_max"],
        "°C"
    )

    print(
        "Minimum Temperature:",
        result["temperature_min"],
        "°C"
    )

    print(
        "Weather Code:",
        result["weather_code"]
    )

    print(
        "Source:",
        result["source"]
    )

    print(
        "Status:",
        result["status"]
    )
