"""
Location-to-coordinate mapping for Andhra Pradesh mandals and districts.

Used by the climate service to query Open-Meteo historical weather data.
Coordinates are approximate centroid values for each location.

Sources: Survey of India / Bhuvan GIS portal / OpenStreetMap
Precision: ±0.05 degrees (acceptable for weather API queries)

To add a new location: add an entry to LOCATION_COORDINATES with lowercase key.
"""

LOCATION_COORDINATES = {
    # Prakasam District
    "markapur": {"latitude": 15.735, "longitude": 79.268},
    "ongole": {"latitude": 15.505, "longitude": 80.049},
    "kandukur": {"latitude": 15.215, "longitude": 79.900},
    "chirala": {"latitude": 15.826, "longitude": 80.352},
    "narasaraopet": {"latitude": 16.235, "longitude": 80.051},
    "giddalur": {"latitude": 15.373, "longitude": 79.060},
    "darsi": {"latitude": 15.767, "longitude": 79.678},

    # Guntur District
    "guntur": {"latitude": 16.306, "longitude": 80.436},
    "tenali": {"latitude": 16.238, "longitude": 80.644},
    "bapatla": {"latitude": 15.906, "longitude": 80.466},
    "sattenapalle": {"latitude": 16.395, "longitude": 80.152},
    "piduguralla": {"latitude": 16.475, "longitude": 79.895},
    "ponnur": {"latitude": 16.068, "longitude": 80.547},

    # Krishna District
    "vijayawada": {"latitude": 16.506, "longitude": 80.648},
    "machilipatnam": {"latitude": 16.186, "longitude": 81.134},
    "gudivada": {"latitude": 16.434, "longitude": 80.995},
    "nuzvid": {"latitude": 16.788, "longitude": 80.848},

    # Kurnool District
    "kurnool": {"latitude": 15.828, "longitude": 78.037},
    "adoni": {"latitude": 15.630, "longitude": 77.274},
    "nandyal": {"latitude": 15.479, "longitude": 78.484},
    "atmakur": {"latitude": 15.873, "longitude": 78.596},

    # Anantapur District
    "anantapur": {"latitude": 14.682, "longitude": 77.600},
    "dharmavaram": {"latitude": 14.413, "longitude": 77.718},
    "hindupur": {"latitude": 13.829, "longitude": 77.492},
    "kadiri": {"latitude": 14.113, "longitude": 78.162},
    "guntakal": {"latitude": 15.172, "longitude": 77.376},

    # Kadapa District
    "kadapa": {"latitude": 14.467, "longitude": 78.822},
    "proddatur": {"latitude": 14.749, "longitude": 78.548},
    "badvel": {"latitude": 14.744, "longitude": 79.060},
    "pulivendla": {"latitude": 14.420, "longitude": 78.227},

    # Nellore District
    "nellore": {"latitude": 14.442, "longitude": 79.987},
    "kavali": {"latitude": 14.916, "longitude": 79.994},
    "gudur": {"latitude": 14.152, "longitude": 79.853},
    "venkatagiri": {"latitude": 13.960, "longitude": 79.581},

    # East Godavari District
    "kakinada": {"latitude": 16.981, "longitude": 82.241},
    "rajahmundry": {"latitude": 17.005, "longitude": 81.804},
    "amalapuram": {"latitude": 16.576, "longitude": 82.000},
    "peddapuram": {"latitude": 17.079, "longitude": 82.133},

    # West Godavari District
    "eluru": {"latitude": 16.714, "longitude": 81.095},
    "bhimavaram": {"latitude": 16.543, "longitude": 81.522},
    "tadepalligudem": {"latitude": 16.813, "longitude": 81.527},
    "kovvur": {"latitude": 17.020, "longitude": 81.727},

    # Visakhapatnam District
    "visakhapatnam": {"latitude": 17.686, "longitude": 83.218},
    "vizag": {"latitude": 17.686, "longitude": 83.218},
    "anakapalle": {"latitude": 17.690, "longitude": 82.999},
    "narsipatnam": {"latitude": 17.670, "longitude": 82.610},

    # Srikakulam District
    "srikakulam": {"latitude": 18.297, "longitude": 83.896},
    "narasannapeta": {"latitude": 18.420, "longitude": 84.044},
    "palasa": {"latitude": 18.770, "longitude": 84.415},

    # Vizianagaram District
    "vizianagaram": {"latitude": 18.115, "longitude": 83.411},
    "bobbili": {"latitude": 18.570, "longitude": 83.360},
    "parvathipuram": {"latitude": 18.784, "longitude": 83.424},

    # Common alternate spellings / short names
    "markapuram": {"latitude": 15.735, "longitude": 79.268},
    "ongol": {"latitude": 15.505, "longitude": 80.049},
}


def get_coordinates(location: str):
    """
    Return lat/lon for a location string.
    Tries exact match first, then partial match.
    Returns error dict if location not found.
    """
    location_clean = location.lower().strip()

    # Exact match
    if location_clean in LOCATION_COORDINATES:
        return {
            "location": location_clean,
            **LOCATION_COORDINATES[location_clean]
        }

    # Partial match: check if any known location is a substring of the input
    for known_location, coords in LOCATION_COORDINATES.items():
        if known_location in location_clean or location_clean in known_location:
            return {
                "location": known_location,
                "matched_from": location_clean,
                **coords
            }

    return {
        "error": (
            f"No coordinates available for '{location}'. "
            f"Supported locations include: {', '.join(sorted(LOCATION_COORDINATES.keys())[:10])}... "
            f"(and {len(LOCATION_COORDINATES) - 10} more)"
        )
    }
