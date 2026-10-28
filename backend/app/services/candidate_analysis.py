"""
Candidate Analysis — runs all crops in CROPS through suitability + market + profit.

This module is the single place where all crop candidates are evaluated
deterministically before being passed to the ranking engine.
"""

from app.crop_data import CROPS
from app.services.crop_suitability import calculate_suitability
from app.tools.market_analysis_tool import market_analysis_tool
from app.tools.profit_tool import profit_calculator_tool


def analyze_all_candidates(
    soil: str,
    water: str,
    season: str,
    temperature: float,
    rainfall: float,
    land_area: float,
    state: str = "Andhra Pradesh",
    budget: float | None = None,
) -> list[dict]:
    """
    Evaluate every crop in the database for:
      1. Agronomic suitability (soil, water, season, temperature, rainfall)
      2. Current market price and historical analysis
      3. Financial projection (profit, ROI, break-even, scenarios)

    Parameters
    ----------
    soil, water, season : farmer's conditions
    temperature         : current or typical temperature in °C
    rainfall            : historical seasonal rainfall in mm
    land_area           : farmer's total land in acres
    state               : state for market price lookups
    budget              : optional farmer budget in Rs (used by ranking engine)

    Returns
    -------
    List of dicts, one per crop, containing suitability, market, and profit data.
    """
    results = []

    for crop_name, crop in CROPS.items():

        # -----------------------------------------------------------------
        # CROP SUITABILITY
        # -----------------------------------------------------------------
        suitability = calculate_suitability(
            crop_name=crop_name,
            soil=soil,
            water=water,
            season=season,
            temperature=temperature,
            rainfall=rainfall,
        )

        # -----------------------------------------------------------------
        # MARKET ANALYSIS
        # -----------------------------------------------------------------
        market_analysis = market_analysis_tool(
            crop=crop_name,
            state=state
        )

        current_market = market_analysis.get("current", {})

        # -----------------------------------------------------------------
        # PROFIT CALCULATION
        # Only calculate when a real market price is available.
        # Pass min/max prices for scenario analysis.
        # -----------------------------------------------------------------
        modal_price = current_market.get("modal_price")
        min_price = current_market.get("min_price")
        max_price = current_market.get("max_price")

        if isinstance(modal_price, (int, float)):
            profit = profit_calculator_tool(
                crop=crop_name,
                yield_per_acre=crop["yield_per_acre"],
                expected_price=modal_price,
                cost_per_acre=crop["cost_per_acre"],
                land_area=land_area,
                min_price=min_price if isinstance(min_price, (int, float)) else None,
                max_price=max_price if isinstance(max_price, (int, float)) else None,
            )
        else:
            # Partial result — cost is known, revenue/profit are not
            total_cost = crop["cost_per_acre"] * land_area
            expected_yield = crop["yield_per_acre"] * land_area
            cost_per_kg = (
                round(crop["cost_per_acre"] / crop["yield_per_acre"], 2)
                if crop["yield_per_acre"] > 0 else None
            )
            break_even_price = (
                round(total_cost / expected_yield, 2)
                if expected_yield > 0 else None
            )
            profit = {
                "crop": crop_name,
                "land_area": land_area,
                "yield_per_acre": crop["yield_per_acre"],
                "expected_yield": expected_yield,
                "yield_unit": "kg/acre",
                "total_yield_unit": "kg",
                "expected_price": None,
                "price_unit": "Rs/kg",
                "price_per_quintal": None,
                "cost_per_acre": crop["cost_per_acre"],
                "cost_per_kg": cost_per_kg,
                "revenue": None,
                "total_cost": total_cost,
                "profit": None,
                "roi_percent": None,
                "break_even_price": break_even_price,
                "scenarios": None,
                "status": "unavailable",
            }

        results.append({
            "crop": crop_name,
            "suitability": suitability,
            "market": market_analysis,
            "profit": profit,
            "budget": budget,
        })

    return results
