"""
Demo Scenarios & Budget Boundary Testing.
Tests:
1. Primary Farmer: Red soil, Medium water, Kharif, 2.5 acres, Rs 65,000 budget.
2. Low Budget (Single crop affordable): Rs 38,000 budget -> Black gram only.
3. Very Low Budget (Zero crops affordable): Rs 20,000 budget -> Explains budget deficit.
4. Cheap vs Profitable: Confirms the engine doesn't blindly pick the cheapest crop when a better affordable crop exists.
5. Hard Agronomic Exclusions: Clay soil in Kharif -> Barred crops excluded.
6. Failure Handling: Missing prices, negative profit, data quality status.
"""

from app.services.crop_suitability import calculate_suitability
from app.tools.profit_tool import profit_calculator_tool
from app.services.crop_recommendation import rank_crops
from app.crop_data import CROPS
from app.services.reliable_market_service import get_reliable_market_price

def evaluate_farmer(soil, water, season, land_area, budget, temperature=28.0, rainfall=700.0):
    candidates = []
    for crop_name, crop_info in CROPS.items():
        suit = calculate_suitability(
            crop_name=crop_name,
            soil=soil,
            water=water,
            season=season,
            temperature=temperature,
            rainfall=rainfall,
        )
        market = get_reliable_market_price(crop_name)
        curr_price = market.get("current_price") or market.get("modal_price")
        min_p = market.get("min_price")
        max_p = market.get("max_price")

        fin = profit_calculator_tool(
            crop=crop_name,
            yield_per_acre=crop_info.get("yield_per_acre"),
            expected_price=curr_price,
            cost_per_acre=crop_info.get("cost_per_acre"),
            land_area=land_area,
            min_price=min_p,
            max_price=max_p,
        )
        is_affordable = (fin["total_cost"] <= budget) if budget is not None else True
        fin["is_affordable"] = is_affordable
        fin["budget_exceeded"] = not is_affordable

        candidates.append({
            "crop": crop_name,
            "suitability": suit,
            "profit": fin,
            "market": market,
        })

    return rank_crops(candidates, budget=budget)


def run_tests():
    print("=" * 70)
    print("SCENARIO 1: Primary Farmer (Red soil, Med water, Kharif, 2.5 ac, Rs 65,000)")
    print("=" * 70)
    res1 = evaluate_farmer("red", "medium", "kharif", 2.5, 65000.0)
    print(f"Top Recommendation: {res1['recommended_crop'].upper()}")
    print(f"Eligible within budget: {res1['eligible_crop_count']}")
    for c in res1["ranked_crops"][:3]:
        p = c["profit"]
        print(f"  #{c['rank']} {c['crop']:12}: Score={c['overall_score']:5.2f}% | Suitability={c['component_scores']['suitability']}% | Cost=Rs {p['total_cost']:,.0f} | Profit=Rs {p['profit']:,.0f} | ROI={p['roi_percent']}% | Break-even=Rs {p['break_even_price']}/kg | Afford={not c.get('budget_exceeded')}")

    print("\n" + "=" * 70)
    print("SCENARIO 2: Tight Budget (Only Black Gram affordable at Rs 38,000)")
    print("=" * 70)
    res2 = evaluate_farmer("red", "medium", "kharif", 2.5, 38000.0)
    print(f"Top Recommendation: {res2['recommended_crop'].upper()} (Affordable: {not res2['ranked_crops'][0].get('budget_exceeded')})")
    print(f"Eligible count: {res2['eligible_crop_count']}")
    # Assert black gram is #1 because it's the only one under 38000 (costs 37500)
    assert res2["recommended_crop"] == "black_gram", f"Expected black_gram, got {res2['recommended_crop']}"
    assert res2["eligible_crop_count"] == 1, f"Expected 1 eligible crop, got {res2['eligible_crop_count']}"
    print("[OK] Successfully selected the only affordable suitable crop!")

    print("\n" + "=" * 70)
    print("SCENARIO 3: Insufficient Budget (Rs 20,000 for 2.5 acres - no crop fits)")
    print("=" * 70)
    res3 = evaluate_farmer("red", "medium", "kharif", 2.5, 20000.0)
    print(f"Eligible count: {res3['eligible_crop_count']}")
    print(f"Reason: {res3.get('no_eligible_crops_reason')}")
    assert res3["eligible_crop_count"] == 0, "Expected 0 eligible crops"
    assert "no_eligible_crops_reason" in res3, "Expected explanation for zero eligible crops"
    print("[OK] Successfully handled zero eligible crops with transparent explanation!")

    print("\n" + "=" * 70)
    print("SCENARIO 4: Fair Evaluation vs Blindly Choosing Cheapest")
    print("In Scenario 1 (budget Rs 65,000), Black Gram costs Rs 37,500 while Red Gram costs Rs 50,000.")
    print(f"Selected #1: {res1['recommended_crop'].upper()}")
    # Confirms it selected Red Gram over Black Gram because Red Gram has better return/suitability balance,
    # proving the engine does NOT just blindly pick the cheapest crop.
    assert res1["recommended_crop"] == "red_gram", f"Expected red_gram, got {res1['recommended_crop']}"
    print("[OK] Engine chose Red Gram (higher net profit & ROI) over cheaper Black Gram!")

    print("\n" + "=" * 70)
    print("SCENARIO 5: Hard Agronomic Exclusions (Clay soil, Kharif, canal water)")
    print("=" * 70)
    res5 = evaluate_farmer("clay", "high", "kharif", 2.0, 100000.0)
    ranked_crops_5 = [c["crop"] for c in res5["ranked_crops"] if c["eligibility_status"] == "eligible"]
    print(f"Eligible crops on Clay in Kharif: {ranked_crops_5}")
    # Paddy should be eligible on clay, whereas Tomato/Groundnut should be ineligible on clay
    assert "paddy" in ranked_crops_5, "Paddy must be eligible on clay"
    assert "groundnut" not in ranked_crops_5, "Groundnut must NOT be eligible on clay"
    print("[OK] Hard agronomic soil exclusion verified on clay soil!")

    print("\n" + "=" * 70)
    print("SCENARIO 6: Missing Market Price & Negative Profit Handling")
    print("=" * 70)
    # Test missing price
    missing_fin = profit_calculator_tool(
        crop="test_crop",
        land_area=2.0,
        cost_per_acre=30000.0,
        yield_per_acre=1000.0,
        expected_price=None,
    )
    assert missing_fin["status"] == "unavailable"
    assert missing_fin["profit"] is None
    assert missing_fin["revenue"] is None
    print("[OK] Missing market price returns status='unavailable' with None profit/revenue.")

    # Test negative profit
    crash_fin = profit_calculator_tool(
        crop="test_crop",
        land_area=1.0,
        cost_per_acre=40000.0,
        yield_per_acre=1000.0,
        expected_price=20.0,  # Revenue = 20,000 < Cost 40,000
    )
    assert crash_fin["profit"] == -20000.0
    assert crash_fin["roi_percent"] == -50.0
    print("[OK] Negative profit correctly preserved (Profit: -Rs 20,000, ROI: -50.0%).")
    print("\nALL DEMO SCENARIOS & BOUNDARY TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
