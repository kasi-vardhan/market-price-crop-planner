from app.services.climate import (
    get_historical_rainfall
)


result = get_historical_rainfall(
    location="Markapur",
    season="kharif",
    years=3
)

print(result)
