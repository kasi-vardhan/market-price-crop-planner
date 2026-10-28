import os
import requests
from dotenv import load_dotenv

load_dotenv()

DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
DATA_GOV_RESOURCE_URL = os.getenv("DATA_GOV_RESOURCE_URL")


import time

_LAST_FAILURE_TIME = 0.0
_FAILURE_COOLDOWN_SECONDS = 60.0


def fetch_market_data(
    state="Andhra Pradesh",
    commodity=None,
    limit=100
):
    """
    Fetch market data from the verified
    Government of India OGD API.
    """
    global _LAST_FAILURE_TIME

    if not DATA_GOV_API_KEY:
        return {
            "status": "unavailable",
            "error": "DATA_GOV_API_KEY is not configured."
        }

    if not DATA_GOV_RESOURCE_URL:
        return {
            "status": "unavailable",
            "error": "DATA_GOV_RESOURCE_URL is not configured."
        }

    # Circuit breaker: if the upstream API recently failed or was unreachable,
    # quickly return unavailable to allow instant fallback to cache without blocking.
    if time.time() - _LAST_FAILURE_TIME < _FAILURE_COOLDOWN_SECONDS:
        return {
            "status": "unavailable",
            "error": "Market API is temporarily unreachable; fallback in effect."
        }

    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": limit
    }

    if state:
        params["filters[state]"] = state

    if commodity:
        params["filters[commodity]"] = commodity

    try:
        response = requests.get(
            DATA_GOV_RESOURCE_URL,
            params=params,
            timeout=3.0
        )
        response.raise_for_status()

    except requests.Timeout:
        _LAST_FAILURE_TIME = time.time()
        return {
            "status": "unavailable",
            "error": "Market API request timed out."
        }

    except requests.RequestException as error:
        _LAST_FAILURE_TIME = time.time()
        return {
            "status": "unavailable",
            "error": f"Market API request failed: {error}"
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "status": "unavailable",
            "error": "Market API returned invalid JSON."
        }

    records = data.get("records", [])

    if not isinstance(records, list):
        return {
            "status": "unavailable",
            "error": "Market API returned an invalid records structure."
        }

    return {
        "status": "live",
        "source": "Government of India OGD",
        "count": len(records),
        "records": records
    }
