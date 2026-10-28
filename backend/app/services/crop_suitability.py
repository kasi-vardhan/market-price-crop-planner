"""
Crop Suitability Assessment Engine.

Evaluates how well a crop matches a farmer's conditions across five dimensions:
  - Soil compatibility      (essential constraint)
  - Season compatibility    (essential constraint)
  - Water availability      (important)
  - Temperature suitability (continuous score)
  - Rainfall suitability    (continuous score)

Returns a structured result with:
  - overall suitability score (0–100)
  - individual component scores
  - eligibility_status: "eligible" | "ineligible" | "marginal"
  - essential_constraint_violations (reasons for ineligibility)
  - reasons (positive and negative)
  - warnings
  - crop requirements
  - data quality notes

Weights (configurable, must sum to 1.0):
  soil        0.25  (essential hard constraint)
  water       0.20
  season      0.15  (essential hard constraint)
  temperature 0.20
  rainfall    0.20
"""

from app.crop_data import CROPS

# ---------------------------------------------------------------------------
# SCORING WEIGHTS
# These are tunable initial weights. Soil and season are also treated as
# essential hard constraints independently.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "soil": 0.25,
    "water": 0.20,
    "season": 0.15,
    "temperature": 0.20,
    "rainfall": 0.20,
}

# A suitability score below this threshold is rated "low" regardless of eligibility
LOW_THRESHOLD = 60.0
HIGH_THRESHOLD = 80.0


def normalize_label(value: str) -> str:
    """Normalize common UI labels and aliases to consistent internal values."""
    value = str(value or "").strip().lower()
    aliases = {
        "red soil": "red",
        "black soil": "black",
        "black cotton soil": "black",
        "alluvial soil": "alluvial",
        "clay soil": "clay",
        "loamy soil": "loamy",
        "sandy soil": "sandy",
        "sandy loam": "sandy",
        "kharif (monsoon)": "kharif",
        "rabi (winter)": "rabi",
        "zaid (summer)": "zaid",
        "summer": "zaid",
        "monsoon": "kharif",
        "winter": "rabi",
        "high (assured irrigation/canal/borewell)": "high",
        "medium (moderate canal/seasonal well)": "medium",
        "low (rainfed / scanty)": "low",
        "low (rainfed/scanty)": "low",
        "rainfed": "low",
        "irrigated": "high",
        "canal": "high",
    }
    return aliases.get(value, value)


def calculate_range_score(value, minimum, maximum) -> float:
    """
    Score a value against an acceptable range [minimum, maximum].

    Inside range  → 100
    Up to 1× range-width outside → degrades linearly toward 0
    Beyond that   → 0

    Missing value → 0 (conservative: not rewarded for unknown data)
    """
    if value is None:
        return 0.0

    try:
        val = float(value)
        min_val = float(minimum)
        max_val = float(maximum)
    except (TypeError, ValueError):
        return 0.0

    if min_val <= val <= max_val:
        return 100.0

    range_size = max_val - min_val
    if range_size <= 0:
        return 0.0

    distance = (min_val - val) if val < min_val else (val - max_val)
    score = 100.0 - (distance / range_size) * 100.0
    return round(max(0.0, min(100.0, score)), 2)


def calculate_water_score(farmer_water: str, crop_water: str) -> tuple[float, str, list[str]]:
    """
    Score water availability and return (score, reason, warnings).

    Matching is tiered:
      farmer == crop                    → 100 (perfect match)
      farmer > crop (surplus water)     → 80  (usually manageable)
      farmer one tier below crop        → 30  (shortage warning)
      farmer two tiers below crop       → 0   (critical shortage)
    """
    tier = {"low": 0, "medium": 1, "high": 2}
    farmer_tier = tier.get(farmer_water, -1)
    crop_tier = tier.get(crop_water, -1)

    warnings = []

    if farmer_tier == crop_tier:
        return 100.0, "Water availability matches the crop requirement", []

    if farmer_tier > crop_tier:
        return 80.0, "Water supply exceeds crop requirement (manageable surplus)", []

    diff = crop_tier - farmer_tier
    if diff == 1:
        msg = f"Water availability '{farmer_water}' may be insufficient for crop requirement '{crop_water}'"
        warnings.append(msg)
        return 30.0, "Available water may be insufficient for this crop", warnings

    # diff >= 2
    msg = f"Water availability '{farmer_water}' is significantly below crop requirement '{crop_water}'"
    warnings.append(msg)
    return 0.0, "Water availability is critically insufficient for this crop", warnings


def calculate_suitability(
    crop_name: str,
    soil: str,
    water: str,
    season: str,
    temperature: float | None = None,
    rainfall: float | None = None,
) -> dict:
    """
    Assess how suitable a crop is for the given conditions.

    Returns a structured dict with score, component scores,
    eligibility_status, reasons, warnings, and data quality.
    """
    crop_name = str(crop_name or "").lower().strip()
    crop = CROPS.get(crop_name)

    if not crop:
        return {
            "crop": crop_name,
            "score": 0.0,
            "level": "unknown",
            "eligibility_status": "unknown",
            "essential_constraint_violations": ["Crop data not available in the database"],
            "component_scores": {
                "soil": 0,
                "water": 0,
                "season": 0,
                "temperature": 0.0,
                "rainfall": 0.0,
            },
            "warnings": ["Crop data not available"],
            "requirements": {},
            "reasons": ["Crop data not available"],
            "data_quality": "no_data"
        }

    soil = normalize_label(soil)
    water = normalize_label(water)
    season = normalize_label(season)

    reasons = []
    warnings = []
    essential_violations = []

    # ------------------------------------------------------------------
    # SOIL — Essential hard constraint
    # ------------------------------------------------------------------
    if soil in crop.get("soil", []):
        soil_score = 100.0
        reasons.append(f"Soil type '{soil}' is compatible")
    else:
        soil_score = 0.0
        reason = f"Soil type '{soil}' is not in the preferred soils for this crop ({', '.join(crop.get('soil', []))})"
        reasons.append(reason)
        warnings.append(reason)
        essential_violations.append(f"SOIL: Farmer's {soil} soil is incompatible with this crop")

    # ------------------------------------------------------------------
    # SEASON — Essential hard constraint
    # ------------------------------------------------------------------
    if season in crop.get("seasons", []):
        season_score = 100.0
        reasons.append(f"Season '{season}' is a suitable growing window")
    else:
        season_score = 0.0
        reason = f"Season '{season}' is not a recognized growing window for this crop ({', '.join(crop.get('seasons', []))})"
        reasons.append(reason)
        warnings.append(reason)
        essential_violations.append(f"SEASON: '{season}' is outside this crop's growing seasons")

    # ------------------------------------------------------------------
    # WATER — Important but not a hard exclusion at "medium" vs "low"
    # ------------------------------------------------------------------
    water_score, water_reason, water_warnings = calculate_water_score(water, crop.get("water", "medium"))
    reasons.append(water_reason)
    warnings.extend(water_warnings)

    # ------------------------------------------------------------------
    # TEMPERATURE — Continuous score
    # ------------------------------------------------------------------
    temperature_range = crop.get("temperature", {"min": 15, "max": 35})

    if temperature is None:
        temperature_score = 50.0  # Neutral — data not available, not assumed perfect
        reasons.append("Temperature data not provided; a neutral score is used")
        warnings.append("Temperature not provided; temperature suitability is estimated")
        data_quality = "partial"
    else:
        temperature_score = calculate_range_score(temperature, temperature_range["min"], temperature_range["max"])
        if temperature_score == 100.0:
            reasons.append(f"Temperature ({temperature}°C) is within the optimal range")
        elif temperature_score >= 60.0:
            reasons.append(f"Temperature ({temperature}°C) is close to the preferred range")
        else:
            msg = f"Temperature ({temperature}°C) is outside the preferred range ({temperature_range['min']}–{temperature_range['max']}°C)"
            reasons.append(msg)
            warnings.append(msg)
        data_quality = "complete"

    # ------------------------------------------------------------------
    # RAINFALL — Continuous score
    # ------------------------------------------------------------------
    rainfall_range = crop.get("rainfall", {"min": 500, "max": 1200})

    if rainfall is None:
        rainfall_score = 50.0
        reasons.append("Seasonal rainfall data not provided; a neutral score is used")
        warnings.append("Rainfall not provided; rainfall suitability is estimated")
        data_quality = "partial"
    else:
        rainfall_score = calculate_range_score(rainfall, rainfall_range["min"], rainfall_range["max"])
        if rainfall_score == 100.0:
            reasons.append(f"Seasonal rainfall ({rainfall} mm) is within the optimal range")
        elif rainfall_score >= 60.0:
            reasons.append(f"Seasonal rainfall ({rainfall} mm) is close to the preferred range")
        else:
            msg = f"Seasonal rainfall ({rainfall} mm) is outside the preferred range ({rainfall_range['min']}–{rainfall_range['max']} mm)"
            reasons.append(msg)
            warnings.append(msg)

    # ------------------------------------------------------------------
    # WEIGHTED SCORE
    # ------------------------------------------------------------------
    score = (
        soil_score * WEIGHTS["soil"]
        + water_score * WEIGHTS["water"]
        + season_score * WEIGHTS["season"]
        + temperature_score * WEIGHTS["temperature"]
        + rainfall_score * WEIGHTS["rainfall"]
    )
    score = round(score, 2)

    if score >= HIGH_THRESHOLD:
        level = "high"
    elif score >= LOW_THRESHOLD:
        level = "medium"
    else:
        level = "low"

    # ------------------------------------------------------------------
    # ELIGIBILITY STATUS
    # ------------------------------------------------------------------
    # "eligible"   → no essential violations
    # "marginal"   → water is very low (30) but soil/season are OK
    # "ineligible" → soil or season constraint violated
    if essential_violations:
        eligibility_status = "ineligible"
    elif water_score <= 30:
        eligibility_status = "marginal"
        warnings.append(
            "Water availability is significantly below the crop requirement. "
            "This crop may fail without additional irrigation."
        )
    else:
        eligibility_status = "eligible"

    cultivation_dur = crop.get("cultivation_duration_days")
    data_quality = "complete" if (temperature is not None and rainfall is not None) else "partial"

    return {
        "crop": crop_name,
        "score": score,
        "level": level,
        "eligibility_status": eligibility_status,
        "essential_constraint_violations": essential_violations,
        "component_scores": {
            "soil": soil_score,
            "water": water_score,
            "season": season_score,
            "temperature": temperature_score,
            "rainfall": rainfall_score,
        },
        "warnings": warnings,
        "requirements": {
            "temperature": temperature_range,
            "rainfall": rainfall_range,
            "water": crop.get("water"),
            "soil": crop.get("soil"),
            "seasons": crop.get("seasons"),
        },
        "cultivation_duration_days": cultivation_dur,
        "reasons": reasons,
        "data_quality": data_quality,
        "source": crop.get("source"),
        "confidence": crop.get("confidence", "unknown"),
    }
