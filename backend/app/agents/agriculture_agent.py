from app.tools.market_tool import market_price_tool
from app.tools.weather_tool import weather_tool
from app.tools.crop_tool import crop_suitability_tool
from app.tools.profit_tool import profit_calculator_tool
from app.tools.rag_tool import rag_search_tool
from app.services.market_trend import get_market_trend

from app.crop_data import CROPS


def run_agriculture_agent(
    farmer_question: str,
    location: str,
    soil: str,
    water: str,
    season: str,
    land_area: float
):
    """
    Main agriculture planning agent.

    The agent coordinates:
    - Weather
    - Crop suitability
    - Market intelligence
    - Profit calculation
    - Agricultural knowledge retrieval
    """

    # ------------------------------------------------
    # STEP 1: Get weather
    # ------------------------------------------------

    weather = weather_tool(location)

    if "error" in weather:
        return {
            "error": weather["error"]
        }

    temperature = weather.get("temperature", 25.0)
    rainfall = weather.get("rainfall") or weather.get("daily_rainfall") or weather.get("precipitation") or 0.0

    # ------------------------------------------------
    # STEP 2: Analyze crops
    # ------------------------------------------------

    crop_analysis = []

    for crop_name, crop_data in CROPS.items():

        suitability = crop_suitability_tool(
            crop=crop_name,
            soil=soil,
            water=water,
            season=season,
            temperature=temperature,
            rainfall=rainfall
        )

        market = market_price_tool(crop_name)

        if not market or "error" in market or market.get("status") == "unavailable":
            continue

        expected_price = (
            market.get("modal_price")
            or market.get("current_price")
            or market.get("price")
            or 0
        )
        if not expected_price and "records" in market and market["records"]:
            expected_price = market["records"][0].get("modal_price", 0)

        profit = profit_calculator_tool(
            crop=crop_name,
            yield_per_acre=crop_data["yield_per_acre"],
            expected_price=expected_price,
            cost_per_acre=crop_data["cost_per_acre"],
            land_area=land_area
        )

        trend_data = get_market_trend(crop_name)
        if isinstance(trend_data, dict) and trend_data.get("status") == "available":
            market["trend"] = trend_data.get("trend", "stable")
            market["outlook"] = trend_data.get("outlook", "neutral")
        else:
            market.setdefault("trend", "stable")
            market.setdefault("outlook", "neutral")

        crop_analysis.append({
            "crop": crop_name,
            "suitability": suitability,
            "market": market,
            "profit": profit
        })

    # ------------------------------------------------
    # STEP 3: Rank crops
    # ------------------------------------------------

    crop_analysis.sort(
        key=lambda item: item["suitability"]["score"],
        reverse=True
    )

    # ------------------------------------------------
    # STEP 4: Select best crop
    # ------------------------------------------------

    if not crop_analysis:
        return {
            "error": "No suitable crop data available."
        }

    recommended_crop = crop_analysis[0]["crop"]

    # ------------------------------------------------
    # STEP 5: Search agricultural knowledge
    # ------------------------------------------------

    knowledge = rag_search_tool(
        farmer_question,
        top_k=3
    )

    # ------------------------------------------------
    # STEP 6: Return complete analysis
    # ------------------------------------------------

    return {
        "farmer_question": farmer_question,

        "location": location,

        "farm_details": {
            "soil": soil,
            "water": water,
            "season": season,
            "land_area": land_area
        },

        "weather": weather,

        "recommended_crop": recommended_crop,

        "crop_analysis": crop_analysis,

        "knowledge": knowledge
    }
