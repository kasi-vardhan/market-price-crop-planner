"""
Input validation for farm planning parameters.
Supplements Pydantic model validation with additional business rules.
"""


def validate_farm_inputs(
    soil: str,
    water: str,
    season: str,
    land_area: float,
    budget: float | None = None,
) -> dict:
    """
    Validate core farm inputs and return a structured result.

    Returns
    -------
    {"valid": bool, "errors": list[str], "warnings": list[str]}
    """
    errors = []
    warnings = []

    valid_soils = {"red", "loamy", "black", "sandy", "clay", "alluvial"}
    valid_water = {"low", "medium", "high"}
    valid_seasons = {"kharif", "rabi", "zaid"}

    if str(soil).lower().strip() not in valid_soils:
        errors.append(
            f"Soil must be one of: {', '.join(sorted(valid_soils))}. Got: '{soil}'."
        )

    if str(water).lower().strip() not in valid_water:
        errors.append(
            f"Water availability must be one of: {', '.join(sorted(valid_water))}. Got: '{water}'."
        )

    if str(season).lower().strip() not in valid_seasons:
        errors.append(
            f"Season must be one of: {', '.join(sorted(valid_seasons))}. Got: '{season}'."
        )

    try:
        area = float(land_area)
        if area <= 0:
            errors.append("Land area must be greater than zero.")
        elif area > 1000:
            errors.append("Land area is outside the supported range (max 1000 acres).")
        elif area < 0.1:
            warnings.append("Land area is very small (< 0.1 acre). Results may be less meaningful.")
    except (TypeError, ValueError):
        errors.append("Land area must be a valid number.")

    if budget is not None:
        try:
            b = float(budget)
            if b < 0:
                errors.append("Budget cannot be negative.")
            elif b == 0:
                warnings.append(
                    "Budget is set to zero. All crops will be flagged as over-budget. "
                    "Provide a realistic budget for meaningful affordability assessment."
                )
            elif b < 5000:
                warnings.append(
                    f"Budget of Rs {b:,.0f} is very low. Most crops require at least Rs 10,000–20,000 per acre."
                )
        except (TypeError, ValueError):
            errors.append("Budget must be a valid number.")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
