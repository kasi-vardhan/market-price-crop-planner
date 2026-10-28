"""
End-to-End Execution Trace for Market Price and Crop Planning Helper.
Traces a concrete farmer request through every subsystem:
1. Input Validation
2. Weather & Climate Service
3. Market Price Retrieval (live/cached)
4. 5-Factor Agronomic Suitability Engine
5. Financial Calculator & Scenarios
6. Budget Filtering & Ranking Engine
7. RAG Knowledge Retrieval
8. Response Payload Composition & Frontend Mapping
"""

import json
from app.services.input_validation import validate_farm_inputs
from app.services.agriculture_weather import get_agriculture_weather
from app.services.climate import get_historical_rainfall
from app.services.reliable_market_service import get_reliable_market_price
from app.services.crop_suitability import calculate_suitability
from app.tools.profit_tool import profit_calculator_tool
from app.services.crop_recommendation import rank_crops
from app.rag.retriever import search_knowledge
from app.crop_data import CROPS

def trace_execution():
    request = {
        "location": "Markapur",
        "soil": "red",
        "water": "medium",
        "season": "kharif",
        "land_area": 2.5,
        "budget": 65000.0,
        "farmer_question": "Which crop is best for red soil with 65k budget?"
    }
    
    print("=================================================================")
    print("STEP 1: INPUT VALIDATION")
    print("=================================================================")
    val = validate_farm_inputs(
        soil=request["soil"],
        water=request["water"],
        season=request["season"],
        land_area=request["land_area"],
        budget=request["budget"],
    )
    print(f"Validation Status: {'VALID' if val['valid'] else 'INVALID'}")
    print(f"Errors: {val['errors']}, Warnings: {val['warnings']}")

    print("\n=================================================================")
    print("STEP 2: WEATHER & HISTORICAL CLIMATE RETRIEVAL")
    print("=================================================================")
    agri_weather = get_agriculture_weather(request["location"], request["season"])
    weather = agri_weather["current_weather"]
    climate = agri_weather["historical_climate"]
    print(f"Location: {weather.get('location')}, Temp: {weather.get('temperature')}°C, Rainfall: {weather.get('daily_rainfall')}mm, Status: {weather.get('status')}")
    print(f"Historical Climate ({climate.get('season')}): {climate.get('average_seasonal_rainfall_mm')}mm over {climate.get('years_analyzed')} years ({climate.get('status')})")

    print("\n=================================================================")
    print("STEP 3: CANDIDATE CROPS AGRONOMIC SUITABILITY (5-FACTOR)")
    print("=================================================================")
    suitability_map = {}
    temp = weather.get("temperature")
    rain = climate.get("average_seasonal_rainfall_mm")
    
    for crop_name in CROPS:
        s = calculate_suitability(
            crop_name=crop_name,
            soil=request["soil"],
            water=request["water"],
            season=request["season"],
            temperature=temp,
            rainfall=rain
        )
        suitability_map[crop_name] = s
        status_str = f"[{s['eligibility_status'].upper()}]"
        viol_str = f" (Violations: {s['essential_constraint_violations']})" if s['essential_constraint_violations'] else ""
        print(f"  - {crop_name:12}: Score={s['score']:5.1f} | Level={s['level']:8} | Status={status_str}{viol_str}")

    print("\n=================================================================")
    print("STEP 4: MARKET DATA & FINANCIAL CALCULATIONS (Deterministic)")
    print("=================================================================")
    crop_analysis = []
    
    for crop_name, crop_info in CROPS.items():
        market = get_reliable_market_price(crop_name)
        curr_price = market.get("current_price") or market.get("modal_price")
        min_p = market.get("min_price")
        max_p = market.get("max_price")
        
        fin = profit_calculator_tool(
            crop=crop_name,
            yield_per_acre=crop_info.get("yield_per_acre"),
            expected_price=curr_price,
            cost_per_acre=crop_info.get("cost_per_acre"),
            land_area=request["land_area"],
            min_price=min_p,
            max_price=max_p
        )
        
        # Check affordability
        is_affordable = (fin["total_cost"] <= request["budget"]) if request["budget"] is not None else True
        fin["is_affordable"] = is_affordable
        fin["budget_exceeded"] = not is_affordable
        
        crop_analysis.append({
            "crop": crop_name,
            "suitability": suitability_map[crop_name],
            "profit": fin,
            "market": market,
        })
        
        print(f"  - {crop_name:12}: Cost=Rs {fin['total_cost']:,.0f} | Revenue=Rs {fin['revenue'] or 0:,.0f} | Profit=Rs {fin['profit'] or 0:,.0f} | ROI={fin['roi_percent']}% | Affordable={is_affordable} | Market Status={market.get('status')}")

    print("\n=================================================================")
    print("STEP 5: RECOMMENDATION RANKING ENGINE (Budget & Constraints)")
    print("=================================================================")
    ranking_res = rank_crops(crop_analysis, budget=request["budget"])
    print(f"Top Recommendation: {ranking_res['recommended_crop'].upper()} (Score: {ranking_res['recommendation_score']}%)")
    print(f"Eligible Crop Count within Budget: {ranking_res['eligible_crop_count']}")
    
    print("\nRanked Order:")
    for item in ranking_res["ranked_crops"]:
        crop = item["crop"]
        status = item["eligibility_status"]
        over = "OVER_BUDGET" if item.get("budget_exceeded") else "WITHIN_BUDGET"
        print(f"  Rank #{item['rank']}: {crop:12} | Score={item['overall_score']:5.2f} | Status={status:10} | Budget={over:13} | CompScores={item.get('component_scores')}")

    print("\n=================================================================")
    print("STEP 6: RAG RETRIEVAL FOR TOP RECOMMENDATION")
    print("=================================================================")
    top_crop = ranking_res["recommended_crop"]
    rag_docs = search_knowledge(f"{top_crop} agronomic practices cultivation", top_k=2, crop=top_crop)
    for doc in rag_docs:
        print(f"  Source [{doc.get('source_id')}]: {doc.get('title')} ({doc.get('organization')})")
        print(f"  Excerpt: {doc.get('text')[:120]}...\n")

    print("=================================================================")
    print("TRACE COMPLETED SUCCESSFULLY")
    print("=================================================================")

if __name__ == "__main__":
    trace_execution()
