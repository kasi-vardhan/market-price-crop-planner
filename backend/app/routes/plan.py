"""
Crop Planning API route.

POST /api/plan
  → Validates farmer inputs
  → Calls generate_crop_plan() (LangGraph workflow)
  → Returns structured CropPlanResponse
"""

from fastapi import APIRouter, HTTPException
from app.models.plan import CropPlanRequest, CropPlanResponse
from app.services.plan_service import generate_crop_plan
from app.services.data_confidence import calculate_data_confidence
from app.services.input_validation import validate_farm_inputs
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Crop Planning"]
)


@router.post(
    "/plan",
    response_model=CropPlanResponse
)
def create_crop_plan(request: CropPlanRequest):

    validation = validate_farm_inputs(
        soil=request.soil,
        water=request.water,
        season=request.season,
        land_area=request.land_area,
        budget=request.budget,
    )

    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid farm inputs",
                "errors": validation["errors"]
            }
        )

    try:
        result = generate_crop_plan(
            farmer_question=request.farmer_question,
            location=request.location,
            soil=request.soil,
            water=request.water,
            season=request.season,
            land_area=request.land_area,
            budget=request.budget,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        logger.exception("Crop planning request failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a crop plan right now."
        )

    tool_results = result["tool_results"]
    ranking = result["ranking"]

    weather = None
    market = []
    crop_suitability = []
    profit_analysis = []
    knowledge = []

    for item in tool_results:
        tool_name = item["tool"]
        tool_result = item["result"]

        if tool_name == "get_weather":
            weather = tool_result
        elif tool_name == "get_market_information":
            if isinstance(tool_result, dict):
                market.append(tool_result)
        elif tool_name == "check_crop_suitability":
            if isinstance(tool_result, dict):
                crop_suitability.append(tool_result)
        elif tool_name == "calculate_profit":
            if isinstance(tool_result, dict):
                profit_analysis.append(tool_result)
        elif tool_name == "search_agricultural_knowledge":
            if isinstance(tool_result, list):
                knowledge.extend(tool_result)

    # Guaranteed fallbacks from deterministic ranking engine
    if not weather or not isinstance(weather, dict) or "error" in weather or weather.get("temperature") is None:
        weather = result.get("weather_data")

    if not weather or not isinstance(weather, dict) or "error" in weather or weather.get("temperature") is None:
        from app.tools.weather_tool import weather_tool
        weather = weather_tool(request.location)

    if isinstance(ranking, dict) and "ranked_crops" in ranking:
        if not market:
            for crop_entry in ranking["ranked_crops"]:
                if isinstance(crop_entry.get("market"), dict):
                    market.append(crop_entry["market"])
        if not crop_suitability:
            for crop_entry in ranking["ranked_crops"]:
                if isinstance(crop_entry.get("suitability"), dict):
                    crop_suitability.append(crop_entry["suitability"])
        if not profit_analysis:
            for crop_entry in ranking["ranked_crops"]:
                if isinstance(crop_entry.get("profit"), dict):
                    profit_analysis.append(crop_entry["profit"])

    recommended_crop = None
    recommendation_score = None

    if isinstance(ranking, dict):
        recommended_crop = ranking.get("recommended_crop")
        recommendation_score = ranking.get("recommendation_score")

    # Data status
    data_status = {}

    if isinstance(weather, dict):
        data_status["weather"] = weather.get("status", "unknown")
        data_status["weather_source"] = weather.get("source", "unknown")

    market_statuses = []
    for item in market:
        if isinstance(item, dict):
            market_statuses.append({
                "crop": item.get("crop"),
                "status": item.get("status", "unknown"),
                "source": item.get("source", "unknown"),
            })
    data_status["market"] = market_statuses

    weather_status = "unavailable"
    if isinstance(weather, dict):
        weather_status = weather.get("status", "unknown")

    market_status_list = [
        item.get("status", "unknown")
        for item in market
        if isinstance(item, dict)
    ]

    has_profit_data = any(
        isinstance(item, dict) and item.get("profit") is not None
        for item in profit_analysis
    )

    has_suitability_data = len(crop_suitability) > 0

    source_citations = result.get("source_citations", [])

    climate = result.get("climate_data")
    climate_status = (
        climate.get("status")
        if isinstance(climate, dict)
        else "unavailable"
    )

    data_confidence = calculate_data_confidence(
        weather_status=weather_status,
        climate_status=climate_status,
        market_statuses=market_status_list,
        has_profit_data=has_profit_data,
        has_suitability_data=has_suitability_data,
        knowledge_source_count=len(source_citations),
    )

    eligible_count = None
    no_eligible_reason = None
    if isinstance(ranking, dict):
        eligible_count = ranking.get("eligible_crop_count")
        no_eligible_reason = ranking.get("no_eligible_crops_reason")

    return {
        "question": result.get("question"),
        "location": request.location,
        "recommended_crop": recommended_crop,
        "recommendation_score": recommendation_score,
        "recommendation": result["recommendation"],
        "weather": weather,
        "climate": climate,
        "market": market,
        "crop_suitability": crop_suitability,
        "profit_analysis": profit_analysis,
        "ranking": ranking,
        "knowledge": knowledge,
        "sources": source_citations,
        "data_status": data_status,
        "data_confidence": data_confidence,
        "budget": request.budget,
        "eligible_crop_count": eligible_count,
        "no_eligible_crops_reason": no_eligible_reason,
    }
