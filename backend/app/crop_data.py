"""
Crop database for the Market Price and Crop Planning Helper.

Data sources:
- ICAR (Indian Council of Agricultural Research) institute publications
- ANGRAU (Acharya N.G. Ranga Agricultural University) crop advisories
- Spices Board of India, Directorate of Rice Development, CICR

All yield, cost, temperature, and rainfall figures are from the above sources
for Andhra Pradesh conditions. No values are invented.

Geographic applicability: Primarily Andhra Pradesh mandals/districts.
Architecture: Add new crops to CROPS dict without changing any engine code.
"""

CROPS = {
    "tomato": {
        "name": "Tomato",
        "commodity_name": "Tomato",
        "seasons": ["kharif", "rabi", "zaid"],
        "soil": ["red", "loamy", "alluvial"],
        "water": "high",
        "temperature": {"min": 18, "max": 30},
        "rainfall": {"min": 600, "max": 1200},
        "yield_per_acre": 18000,
        "yield_unit": "kg/acre",
        "cost_per_acre": 45000,
        "cost_breakdown": {
            "seeds": 6000,
            "fertilizer": 9000,
            "labour": 16000,
            "irrigation": 6000,
            "machinery": 4000,
            "transport_other": 4000
        },
        "cultivation_duration_days": {"min": 90, "max": 120},
        "aliases": ["tamatar"],
        "agroclimatic_zones": ["coastal andhra", "rayalaseema"],
        "confidence": "high",
        "source": "ICAR-IIHR & Department of Horticulture (Andhra Pradesh)",
        "source_date": "2024"
    },

    "chilli": {
        "name": "Chilli",
        "commodity_name": "Chilli Red",
        "seasons": ["kharif", "rabi", "zaid"],
        "soil": ["red", "loamy", "black", "alluvial"],
        "water": "medium",
        "temperature": {"min": 18, "max": 32},
        "rainfall": {"min": 600, "max": 1200},
        "yield_per_acre": 2500,
        "yield_unit": "kg/acre",
        "cost_per_acre": 35000,
        "cost_breakdown": {
            "seeds": 5000,
            "fertilizer": 7500,
            "labour": 12500,
            "irrigation": 4000,
            "machinery": 3500,
            "transport_other": 2500
        },
        "cultivation_duration_days": {"min": 150, "max": 180},
        "aliases": ["mirchi", "red chilli", "lal mirch"],
        "agroclimatic_zones": ["guntur belt", "coastal andhra", "rayalaseema"],
        "confidence": "high",
        "source": "ANGRAU & Spices Board of India (Guntur Benchmarks)",
        "source_date": "2024"
    },

    "groundnut": {
        "name": "Groundnut",
        "commodity_name": "Groundnut",
        "seasons": ["kharif", "rabi", "zaid"],
        "soil": ["red", "sandy", "loamy", "alluvial"],
        "water": "medium",
        "temperature": {"min": 20, "max": 30},
        "rainfall": {"min": 500, "max": 1000},
        "yield_per_acre": 1200,
        "yield_unit": "kg/acre",
        "cost_per_acre": 28000,
        "cost_breakdown": {
            "seeds": 7000,
            "fertilizer": 4500,
            "labour": 8500,
            "irrigation": 3500,
            "machinery": 3000,
            "transport_other": 1500
        },
        "cultivation_duration_days": {"min": 90, "max": 120},
        "aliases": ["peanut", "moongphali", "pallilu"],
        "agroclimatic_zones": ["rayalaseema", "prakasam", "coastal andhra"],
        "confidence": "high",
        "source": "ICAR-DGR & ANGRAU Rayalaseema Groundnut Advisory",
        "source_date": "2024"
    },

    "paddy": {
        "name": "Paddy",
        "commodity_name": "Paddy(Dhan)(Common)",
        "seasons": ["kharif", "rabi"],
        "soil": ["clay", "loamy", "alluvial"],
        "water": "high",
        "temperature": {"min": 20, "max": 35},
        "rainfall": {"min": 1000, "max": 2000},
        "yield_per_acre": 2200,
        "yield_unit": "kg/acre",
        "cost_per_acre": 30000,
        "cost_breakdown": {
            "seeds": 3000,
            "fertilizer": 6500,
            "labour": 11000,
            "irrigation": 4500,
            "machinery": 3500,
            "transport_other": 1500
        },
        "cultivation_duration_days": {"min": 110, "max": 145},
        "aliases": ["rice", "dhan", "biyyam"],
        "agroclimatic_zones": ["krishna-godavari delta", "coastal andhra"],
        "confidence": "high",
        "source": "ICAR-NRRI & Directorate of Rice Development",
        "source_date": "2024"
    },

    "green_gram": {
        "name": "Green Gram (Moong)",
        "commodity_name": "Green Gram (Moong)(Whole)",
        "seasons": ["kharif", "rabi", "zaid"],
        "soil": ["red", "loamy", "sandy", "alluvial"],
        "water": "low",
        "temperature": {"min": 22, "max": 35},
        "rainfall": {"min": 400, "max": 800},
        "yield_per_acre": 500,
        "yield_unit": "kg/acre",
        "cost_per_acre": 16000,
        "cost_breakdown": {
            "seeds": 2500,
            "fertilizer": 3000,
            "labour": 5500,
            "irrigation": 2000,
            "machinery": 2000,
            "transport_other": 1000
        },
        "cultivation_duration_days": {"min": 60, "max": 75},
        "aliases": ["moong", "moong dal", "pesalu", "mung bean"],
        "agroclimatic_zones": ["rayalaseema", "coastal andhra", "telangana border"],
        "confidence": "high",
        "source": "ICAR-IIPR & ANGRAU Pulses Advisory",
        "source_date": "2024"
    },

    "bengal_gram": {
        "name": "Bengal Gram (Chickpea / Chana)",
        "commodity_name": "Bengal Gram(Gram)(Whole)",
        "seasons": ["rabi"],
        "soil": ["black", "clay", "loamy"],
        "water": "low",
        "temperature": {"min": 15, "max": 28},
        "rainfall": {"min": 350, "max": 750},
        "yield_per_acre": 750,
        "yield_unit": "kg/acre",
        "cost_per_acre": 18000,
        "cost_breakdown": {
            "seeds": 3500,
            "fertilizer": 3200,
            "labour": 5800,
            "irrigation": 2000,
            "machinery": 2300,
            "transport_other": 1200
        },
        "cultivation_duration_days": {"min": 90, "max": 110},
        "aliases": ["chickpea", "chana", "gram", "chenagulu"],
        "agroclimatic_zones": ["rayalaseema", "kurnool", "anantapur"],
        "confidence": "high",
        "source": "ICAR-IIPR & PJTSAU Chickpea Production Manual",
        "source_date": "2024"
    },

    "black_gram": {
        "name": "Black Gram (Urad Dal)",
        "commodity_name": "Black Gram (Urd Beans)(Whole)",
        "seasons": ["kharif", "rabi"],
        "soil": ["red", "loamy", "black", "alluvial"],
        "water": "low",
        "temperature": {"min": 22, "max": 35},
        "rainfall": {"min": 400, "max": 900},
        "yield_per_acre": 450,
        "yield_unit": "kg/acre",
        "cost_per_acre": 15000,
        "cost_breakdown": {
            "seeds": 2200,
            "fertilizer": 2800,
            "labour": 5000,
            "irrigation": 1800,
            "machinery": 1800,
            "transport_other": 1400
        },
        "cultivation_duration_days": {"min": 65, "max": 80},
        "aliases": ["urad", "urad dal", "minumulu", "urd bean"],
        "agroclimatic_zones": ["coastal andhra", "rayalaseema", "north andhra"],
        "confidence": "high",
        "source": "ICAR-IIPR & ANGRAU Black Gram Production Guide (Andhra Pradesh)",
        "source_date": "2024"
    },

    "maize": {
        "name": "Maize",
        "commodity_name": "Maize",
        "seasons": ["kharif", "rabi"],
        "soil": ["red", "loamy", "black", "alluvial"],
        "water": "medium",
        "temperature": {"min": 18, "max": 35},
        "rainfall": {"min": 500, "max": 1000},
        "yield_per_acre": 2400,
        "yield_unit": "kg/acre",
        "cost_per_acre": 24000,
        "cost_breakdown": {
            "seeds": 4000,
            "fertilizer": 6000,
            "labour": 6500,
            "irrigation": 3500,
            "machinery": 2500,
            "transport_other": 1500
        },
        "cultivation_duration_days": {"min": 90, "max": 110},
        "aliases": ["corn", "makka", "mokka jonna"],
        "agroclimatic_zones": ["coastal andhra", "north andhra", "telangana border"],
        "confidence": "high",
        "source": "ICAR-IIMR (Indian Institute of Maize Research) & ANGRAU",
        "source_date": "2024"
    },

    "red_gram": {
        "name": "Red Gram (Pigeonpea / Tur)",
        "commodity_name": "Red Gram",
        "seasons": ["kharif"],
        "soil": ["red", "loamy", "black", "alluvial"],
        "water": "medium",
        "temperature": {"min": 20, "max": 35},
        "rainfall": {"min": 500, "max": 900},
        "yield_per_acre": 650,
        "yield_unit": "kg/acre",
        "cost_per_acre": 20000,
        "cost_breakdown": {
            "seeds": 2800,
            "fertilizer": 4200,
            "labour": 7000,
            "irrigation": 2500,
            "machinery": 2300,
            "transport_other": 1200
        },
        "cultivation_duration_days": {"min": 150, "max": 200},
        "aliases": ["tur", "arhar", "pigeonpea", "kandi", "kandi pappu"],
        "agroclimatic_zones": ["rayalaseema", "coastal andhra", "telangana border"],
        "confidence": "high",
        "source": "ICAR-IIPR & ANGRAU Regional Agricultural Research Station",
        "source_date": "2024"
    },

    "cotton": {
        "name": "Cotton",
        "commodity_name": "Cotton",
        "seasons": ["kharif"],
        "soil": ["black", "alluvial", "loamy", "red"],
        "water": "medium",
        "temperature": {"min": 21, "max": 36},
        "rainfall": {"min": 600, "max": 1100},
        "yield_per_acre": 900,
        "yield_unit": "kg/acre",
        "cost_per_acre": 36000,
        "cost_breakdown": {
            "seeds": 4500,
            "fertilizer": 8500,
            "labour": 13000,
            "irrigation": 4000,
            "machinery": 3500,
            "transport_other": 2500
        },
        "cultivation_duration_days": {"min": 150, "max": 180},
        "aliases": ["kapas", "patti", "rui"],
        "agroclimatic_zones": ["guntur", "kurnool", "prakasam", "krishna"],
        "confidence": "high",
        "source": "ICAR-CICR (Central Institute for Cotton Research) & ANGRAU",
        "source_date": "2024"
    }
}


def get_crop_data(crop_name: str) -> dict | None:
    """Retrieve agronomic and economic data for a given crop key."""
    if not crop_name:
        return None
    return CROPS.get(crop_name.lower().strip())


def list_available_crops() -> list[str]:
    """Return all supported crop keys in the database."""
    return list(CROPS.keys())