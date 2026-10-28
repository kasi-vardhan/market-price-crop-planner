from app.crop_data import CROPS
from app.services.crop_suitability import calculate_suitability
from app.services.market_intelligence import analyze_market
from app.services.weather import get_weather


def recommend_crops(
    soil,
    water,
    season,
    land_area,
    location
):
    weather_data = get_weather(location)

    if "error" in weather_data:
        return {
            "error": weather_data["error"]
        }

    temperature = weather_data.get("temperature", 28)
    rainfall = weather_data.get("daily_rainfall", 0)

    recommendations = []

    for crop_name, crop in CROPS.items():

        # -------------------------
        # Crop suitability
        # -------------------------

        suitability = calculate_suitability(
            crop_name=crop_name,
            soil=soil,
            water=water,
            season=season,
            temperature=temperature,
            rainfall=rainfall
        )

        score = suitability["score"]
        reasons = suitability["reasons"]

        # -------------------------
        # Market Intelligence (Price + Trend)
        # -------------------------

        market_data = analyze_market(crop_name)

        if "error" not in market_data:
            expected_price = market_data["current_price"]["modal"]
        else:
            expected_price = 0

        # -------------------------
        # Financial calculation
        # -------------------------

        revenue = (
            crop["yield_per_acre"]
            * expected_price
            * land_area
        )

        cost = crop["cost_per_acre"] * land_area

        profit = revenue - cost

        # -------------------------
        # Final result
        # -------------------------

        recommendations.append({
            "crop": crop_name,

            "suitability_score": score,
            "suitability_level": suitability["level"],
            "suitability_reasons": reasons,

            "market": market_data.get("market"),
            "min_price": market_data.get("current_price", {}).get("min"),
            "max_price": market_data.get("current_price", {}).get("max"),
            "expected_price": expected_price,

            "trend": market_data.get("trend"),
            "price_change": market_data.get("price_change"),
            "outlook": market_data.get("outlook"),
            "historical_prices": market_data.get("historical_prices"),

            "revenue": revenue,
            "cost": cost,
            "profit": profit
        })

    # Highest suitability first
    recommendations.sort(
        key=lambda x: x["suitability_score"],
        reverse=True
    )

    return recommendations