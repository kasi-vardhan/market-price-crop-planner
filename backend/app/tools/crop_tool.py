from app.services.crop_suitability import calculate_suitability


def crop_suitability_tool(
    crop: str,
    soil: str,
    water: str,
    season: str,
    temperature: float,
    rainfall: float
):
    """
    Calculate how suitable a crop is
    for the farmer's conditions.
    """

    return calculate_suitability(
        crop_name=crop,
        soil=soil,
        water=water,
        season=season,
        temperature=temperature,
        rainfall=rainfall
    )
