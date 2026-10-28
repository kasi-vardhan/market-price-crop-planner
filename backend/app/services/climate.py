import requests
from datetime import date

from app.services.location_data import get_coordinates


OPEN_METEO_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


SEASON_MONTHS = {
    "kharif": [6, 7, 8, 9, 10],
    "rabi": [11, 12, 1, 2]
}


def get_season_dates(
    season: str,
    year: int
):
    season = season.lower().strip()

    if season == "kharif":

        return (
            date(year, 6, 1),
            date(year, 10, 31)
        )

    if season == "rabi":

        return (
            date(year, 11, 1),
            date(year + 1, 2, 28)
        )

    return None, None


def get_historical_rainfall(
    location: str,
    season: str,
    years: int = 3
):
    """
    Calculate average seasonal rainfall using
    historical Open-Meteo weather data.

    We use completed seasons only.
    """

    coordinates = get_coordinates(
        location
    )

    if "error" in coordinates:
        return coordinates

    current_year = date.today().year

    seasonal_totals = []

    for offset in range(
        1,
        years + 1
    ):

        season_year = (
            current_year - offset
        )

        start_date, end_date = (
            get_season_dates(
                season,
                season_year
            )
        )

        if start_date is None:
            return {
                "status": "unavailable",
                "error": (
                    f"Unsupported season: {season}"
                )
            }

        params = {
            "latitude": coordinates[
                "latitude"
            ],
            "longitude": coordinates[
                "longitude"
            ],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "auto"
        }

        try:

            response = requests.get(
                OPEN_METEO_ARCHIVE_URL,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            return {
                "status": "unavailable",
                "error": (
                    f"Historical weather request "
                    f"failed: {error}"
                )
            }

        except ValueError:

            return {
                "status": "unavailable",
                "error": (
                    "Historical weather API "
                    "returned invalid JSON."
                )
            }

        daily = data.get(
            "daily",
            {}
        )

        rainfall_values = daily.get(
            "precipitation_sum",
            []
        )

        rainfall_values = [
            value
            for value in rainfall_values
            if isinstance(
                value,
                (int, float)
            )
        ]

        if not rainfall_values:
            continue

        total_rainfall = sum(
            rainfall_values
        )

        seasonal_totals.append({
            "season_year": season_year,
            "rainfall_mm": round(
                total_rainfall,
                2
            )
        })

    if not seasonal_totals:

        return {
            "status": "unavailable",
            "location": location,
            "season": season,
            "error": (
                "No historical rainfall data "
                "was available."
            )
        }

    rainfall_values = [
        item["rainfall_mm"]
        for item in seasonal_totals
    ]

    average_rainfall = (
        sum(rainfall_values)
        / len(rainfall_values)
    )

    return {
        "status": "available",
        "location": location,
        "season": season,
        "years_analyzed": len(
            seasonal_totals
        ),
        "historical_years": seasonal_totals,
        "average_seasonal_rainfall_mm": round(
            average_rainfall,
            2
        ),
        "source": "Open-Meteo Historical Weather API"
    }
