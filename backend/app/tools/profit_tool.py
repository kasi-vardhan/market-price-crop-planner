"""
Deterministic financial calculator for crop planning.

Formulas:
  Total Cost       = cost_per_acre × land_area
  Expected Yield   = yield_per_acre × land_area
  Gross Revenue    = expected_yield × expected_price
  Net Profit       = Gross Revenue − Total Cost
  ROI (%)          = (Net Profit / Total Cost) × 100
  Break-even Price = Total Cost / Expected Yield
  Cost per kg      = cost_per_acre / yield_per_acre

No market prices are invented here. A profit figure is only returned
when an actual mandi price is available.
"""


def profit_calculator_tool(
    crop: str,
    yield_per_acre: float,
    expected_price: float,
    cost_per_acre: float,
    land_area: float,
    min_price: float | None = None,
    max_price: float | None = None,
):
    """
    Calculate crop revenue, cost, net profit, and ROI.

    Parameters
    ----------
    crop            : internal crop key (e.g. "tomato")
    yield_per_acre  : expected marketable yield in kg per acre
    expected_price  : modal/expected mandi price in Rs/kg
    cost_per_acre   : total cultivation cost per acre in Rs
    land_area       : farmer's total land in acres
    min_price       : optional minimum mandi price for conservative scenario
    max_price       : optional maximum mandi price for optimistic scenario
    """
    if land_area is not None and land_area <= 0:
        raise ValueError("land_area must be greater than zero")

    if (yield_per_acre is not None and yield_per_acre < 0) or (cost_per_acre is not None and cost_per_acre < 0):
        raise ValueError("Yield and cost cannot be negative")

    land_area_val = land_area if land_area is not None else 1.0
    cost_per_acre_val = cost_per_acre if cost_per_acre is not None else 0.0
    yield_per_acre_val = yield_per_acre if yield_per_acre is not None else 0.0

    total_cost = cost_per_acre_val * land_area_val
    expected_yield = yield_per_acre_val * land_area_val

    # Break-even price: minimum price needed to recover costs
    break_even_price = None
    if expected_yield > 0:
        break_even_price = round(total_cost / expected_yield, 2)

    # Cost per kg
    cost_per_kg = None
    if yield_per_acre_val > 0:
        cost_per_kg = round(cost_per_acre_val / yield_per_acre_val, 2)

    # Never invent a market price or calculate profit without one.
    if expected_price is None:
        return {
            "crop": crop,
            "land_area": land_area_val,
            "yield_per_acre": yield_per_acre_val,
            "expected_yield": expected_yield,
            "yield_unit": "kg/acre",
            "total_yield_unit": "kg",
            "expected_price": None,
            "price_unit": "Rs/kg",
            "price_per_quintal": None,
            "cost_per_acre": cost_per_acre_val,
            "cost_per_kg": cost_per_kg,
            "revenue": None,
            "total_cost": total_cost,
            "profit": None,
            "roi_percent": None,
            "break_even_price": break_even_price,
            "scenarios": None,
            "status": "unavailable",
        }

    if expected_price < 0:
        raise ValueError("expected_price cannot be negative")

    revenue = yield_per_acre_val * expected_price * land_area_val
    profit = revenue - total_cost

    # ROI
    roi_percent = None
    if total_cost > 0:
        roi_percent = round((profit / total_cost) * 100, 2)

    # Profit scenarios (only when min/max price available)
    scenarios = None
    if min_price is not None and max_price is not None:
        conservative_revenue = yield_per_acre_val * min_price * land_area_val
        optimistic_revenue = yield_per_acre_val * max_price * land_area_val
        conservative_profit = conservative_revenue - total_cost
        optimistic_profit = optimistic_revenue - total_cost
        scenarios = {
            "conservative": {
                "price": min_price,
                "revenue": round(conservative_revenue, 2),
                "profit": round(conservative_profit, 2),
                "roi_percent": round((conservative_profit / total_cost) * 100, 2) if total_cost > 0 else None
            },
            "expected": {
                "price": expected_price,
                "revenue": round(revenue, 2),
                "profit": round(profit, 2),
                "roi_percent": roi_percent
            },
            "optimistic": {
                "price": max_price,
                "revenue": round(optimistic_revenue, 2),
                "profit": round(optimistic_profit, 2),
                "roi_percent": round((optimistic_profit / total_cost) * 100, 2) if total_cost > 0 else None
            },
            "assumption": (
                "Scenarios use AGMARKNET min/max price range. "
                "Actual prices at time of sale may differ."
            )
        }

    return {
        "crop": crop,
        "land_area": land_area_val,
        "yield_per_acre": yield_per_acre_val,
        "expected_yield": expected_yield,
        "yield_unit": "kg/acre",
        "total_yield_unit": "kg",
        "expected_price": expected_price,
        "price_unit": "Rs/kg",
        "price_per_quintal": round(expected_price * 100, 2),
        "cost_per_acre": cost_per_acre_val,
        "cost_per_kg": cost_per_kg,
        "revenue": round(revenue, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "roi_percent": roi_percent,
        "break_even_price": break_even_price,
        "scenarios": scenarios,
        "status": "calculated",
    }
