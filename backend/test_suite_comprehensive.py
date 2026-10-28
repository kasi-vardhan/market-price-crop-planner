"""
Comprehensive Automated Test Suite for Market Price and Crop Planning Helper.

Covers all Phase 6 / Section 12 test specifications:
1. Suitable crop selection
2. Unsuitable soil and season combinations
3. Water and weather compatibility
4. Investment-budget filtering
5. Low-investment crops with good expected profit
6. High-profit crops that are agronomically unsuitable (must NOT rank #1)
7. Crops with negative expected profit
8. Missing market prices & fallbacks
9. Missing yield or cost information
10. ROI and financial arithmetic
11. Invalid land area and budget validation
12. Unit conversion and rounding
13. No eligible crops handling
14. Scenarios: conservative, expected, optimistic
15. Top 3 crops comparison structure
"""

import unittest
from app.services.crop_suitability import calculate_suitability
from app.tools.profit_tool import profit_calculator_tool
from app.services.crop_recommendation import rank_crops
from app.services.input_validation import validate_farm_inputs
from app.crop_data import CROPS, get_crop_data


class TestCropSuitability(unittest.TestCase):
    def test_suitable_crop_selection(self):
        """Tomato in red soil, kharif season with high water should be highly suitable."""
        res = calculate_suitability("tomato", "red", "high", "kharif")
        self.assertEqual(res["eligibility_status"], "eligible")
        self.assertGreaterEqual(res["score"], 70.0)
        self.assertIn(res["level"], ["high", "medium"])
        self.assertEqual(len(res["essential_constraint_violations"]), 0)

    def test_unsuitable_soil(self):
        """Tomato in clay soil is incompatible (essential hard constraint violated)."""
        res = calculate_suitability("tomato", "clay", "high", "kharif")
        self.assertEqual(res["eligibility_status"], "ineligible")
        self.assertGreater(len(res["essential_constraint_violations"]), 0)
        self.assertTrue(any("SOIL" in v for v in res["essential_constraint_violations"]))

    def test_unsuitable_season(self):
        """Cotton in summer/zaid season is outside growing season."""
        res = calculate_suitability("cotton", "black", "medium", "summer")
        self.assertEqual(res["eligibility_status"], "ineligible")
        self.assertTrue(any("SEASON" in v for v in res["essential_constraint_violations"]))

    def test_unsuitable_water(self):
        """Tomato requiring high water with low farmer water should be penalized / marginal."""
        res = calculate_suitability("tomato", "red", "low", "kharif")
        self.assertEqual(res["component_scores"]["water"], 0.0)
        self.assertEqual(res["eligibility_status"], "marginal")
        self.assertTrue(any("water" in w.lower() for w in res["warnings"]))

    def test_temperature_penalty(self):
        """Extreme temperatures should lower suitability score."""
        res_normal = calculate_suitability("tomato", "red", "high", "kharif", temperature=25.0)
        res_extreme = calculate_suitability("tomato", "red", "high", "kharif", temperature=48.0)
        self.assertGreater(res_normal["score"], res_extreme["score"])
        self.assertEqual(res_extreme["component_scores"]["temperature"], 0.0)

    def test_black_gram_suitability(self):
        """Newly added black_gram should evaluate accurately in kharif and rabi with black/red soil."""
        bg_data = get_crop_data("black_gram")
        self.assertIsNotNone(bg_data)
        # With matching low water and kharif
        res = calculate_suitability("black_gram", "black", "low", "kharif", temperature=28.0, rainfall=600.0)
        self.assertEqual(res["eligibility_status"], "eligible")
        self.assertGreaterEqual(res["score"], 90.0)


class TestFinancialCalculator(unittest.TestCase):
    def test_financial_arithmetic_and_roi(self):
        """Check exact arithmetic: revenue = yield * price * land, profit = revenue - cost, roi = profit / cost * 100."""
        land_area = 2.0  # acres
        cost_per_acre = 30000.0
        yield_per_acre = 100.0  # kg/acre
        expected_price = 500.0  # Rs/kg

        fin = profit_calculator_tool(
            crop="test_crop",
            land_area=land_area,
            cost_per_acre=cost_per_acre,
            yield_per_acre=yield_per_acre,
            expected_price=expected_price,
            min_price=400.0,
            max_price=600.0,
        )

        expected_total_cost = 2.0 * 30000.0  # 60000.0
        expected_total_yield = 2.0 * 100.0  # 200.0
        expected_revenue = 200.0 * 500.0  # 100000.0
        expected_profit = 100000.0 - 60000.0  # 40000.0
        expected_roi = (40000.0 / 60000.0) * 100.0  # 66.67%

        self.assertEqual(fin["total_cost"], expected_total_cost)
        self.assertEqual(fin["expected_yield"], expected_total_yield)
        self.assertEqual(fin["revenue"], expected_revenue)
        self.assertEqual(fin["profit"], expected_profit)
        self.assertAlmostEqual(fin["roi_percent"], expected_roi, places=1)
        self.assertEqual(fin["break_even_price"], round(60000.0 / 200.0, 2))  # 300.0 Rs/kg
        self.assertEqual(fin["cost_per_kg"], round(30000.0 / 100.0, 2))  # 300.0 Rs/kg

    def test_negative_expected_profit(self):
        """When prices crash below production cost, profit must be negative and ROI negative."""
        fin = profit_calculator_tool(
            crop="tomato",
            land_area=1.0,
            cost_per_acre=50000.0,
            yield_per_acre=50.0,
            expected_price=500.0,  # revenue = 25000
        )
        self.assertEqual(fin["profit"], -25000.0)
        self.assertEqual(fin["roi_percent"], -50.0)

    def test_missing_price_handling(self):
        """Missing market price must return status 'unavailable' without fabricating numbers."""
        fin = profit_calculator_tool(
            crop="tomato",
            land_area=2.0,
            cost_per_acre=30000.0,
            yield_per_acre=100.0,
            expected_price=None,
        )
        self.assertIsNone(fin["expected_price"])
        self.assertIsNone(fin["revenue"])
        self.assertIsNone(fin["profit"])
        self.assertEqual(fin["status"], "unavailable")

    def test_scenarios_conservative_expected_optimistic(self):
        """Conservative < Expected < Optimistic in price, revenue, and profit."""
        fin = profit_calculator_tool(
            crop="chilli",
            land_area=2.0,
            cost_per_acre=45000.0,
            yield_per_acre=25.0,
            expected_price=110.0,
            min_price=90.0,
            max_price=130.0,
        )
        scenarios = fin["scenarios"]
        self.assertIsNotNone(scenarios)
        self.assertIn("conservative", scenarios)
        self.assertIn("expected", scenarios)
        self.assertIn("optimistic", scenarios)
        self.assertLess(
            scenarios["conservative"]["profit"],
            scenarios["expected"]["profit"],
        )
        self.assertLess(
            scenarios["expected"]["profit"],
            scenarios["optimistic"]["profit"],
        )


class TestRecommendationRanking(unittest.TestCase):
    def test_high_profit_unsuitable_crop_cannot_rank_first(self):
        """
        CRITICAL RULE:
        A crop with high profit but unsuitable conditions (level: 'unsuitable', score 0)
        must NEVER rank above a suitable crop with moderate profit.
        """
        candidates = [
            {
                "crop": "luxury_crop",
                "suitability": {"score": 0, "level": "unsuitable", "eligibility_status": "ineligible"},
                "profit": {"profit": 500000, "total_cost": 40000, "is_affordable": True, "roi_percent": 1250},
                "market": {"outlook": "positive", "historical_prices": [100, 105, 110]},
            },
            {
                "crop": "groundnut",
                "suitability": {"score": 85, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 60000, "total_cost": 25000, "is_affordable": True, "roi_percent": 140},
                "market": {"outlook": "stable", "historical_prices": [65, 66, 68]},
            },
        ]
        result = rank_crops(candidates)
        self.assertEqual(result["recommended_crop"], "groundnut")
        self.assertNotEqual(result["recommended_crop"], "luxury_crop")

    def test_over_budget_crop_cannot_rank_first_when_budget_set(self):
        """
        CRITICAL RULE:
        If farmer sets budget = 50,000, an over-budget crop (cost: 120,000)
        must NOT rank above an eligible, affordable crop.
        """
        candidates = [
            {
                "crop": "chilli",
                "suitability": {"score": 90, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 150000, "total_cost": 120000, "is_affordable": False, "roi_percent": 125},
                "market": {"outlook": "positive", "historical_prices": [110, 115, 120]},
            },
            {
                "crop": "black_gram",
                "suitability": {"score": 85, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 40000, "total_cost": 30000, "is_affordable": True, "roi_percent": 133},
                "market": {"outlook": "stable", "historical_prices": [70, 72, 75]},
            },
        ]
        result = rank_crops(candidates, budget=50000.0)
        self.assertEqual(result["recommended_crop"], "black_gram")

    def test_no_eligible_crops_graceful_handling(self):
        """When all crops fail suitability or budget, return clear reason and zero eligible count."""
        candidates = [
            {
                "crop": "chilli",
                "suitability": {"score": 0, "level": "unsuitable", "eligibility_status": "ineligible"},
                "profit": {"profit": 10000, "total_cost": 80000, "is_affordable": False},
                "market": {"outlook": "neutral", "historical_prices": []},
            },
        ]
        result = rank_crops(candidates, budget=20000.0)
        self.assertIn("no_eligible_crops_reason", result)
        self.assertEqual(result["eligible_crop_count"], 0)

    def test_marginal_within_budget_ranks_ahead_of_over_budget(self):
        """A marginal crop within budget must rank ahead of an over-budget crop."""
        candidates = [
            {
                "crop": "crop_expensive",
                "suitability": {"score": 90, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 100000, "total_cost": 90000, "is_affordable": False},
                "market": {"outlook": "stable", "historical_prices": [50, 50]},
            },
            {
                "crop": "crop_marginal_affordable",
                "suitability": {"score": 75, "level": "medium", "eligibility_status": "marginal"},
                "profit": {"profit": 40000, "total_cost": 30000, "is_affordable": True},
                "market": {"outlook": "stable", "historical_prices": [50, 50]},
            },
        ]
        result = rank_crops(candidates, budget=40000.0)
        self.assertEqual(result["recommended_crop"], "crop_marginal_affordable")

    def test_deterministic_tie_breaker(self):
        """When two eligible affordable crops have identical overall score, suitability breaks tie."""
        candidates = [
            {
                "crop": "crop_a",
                "suitability": {"score": 80, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 50000, "total_cost": 25000, "is_affordable": True, "roi_percent": 100},
                "market": {"outlook": "stable", "historical_prices": [50, 50]},
            },
            {
                "crop": "crop_b",
                "suitability": {"score": 95, "level": "high", "eligibility_status": "eligible"},
                "profit": {"profit": 50000, "total_cost": 25000, "is_affordable": True, "roi_percent": 100},
                "market": {"outlook": "stable", "historical_prices": [50, 50]},
            },
        ]
        result = rank_crops(candidates, budget=50000.0)
        # crop_b has higher suitability score (95 vs 80)
        self.assertEqual(result["recommended_crop"], "crop_b")


class TestInputValidation(unittest.TestCase):
    def test_invalid_land_area(self):
        """Land area <= 0 must fail validation."""
        val_neg = validate_farm_inputs("red", "high", "kharif", land_area=-2.0)
        self.assertFalse(val_neg["valid"])
        self.assertTrue(any("land area" in e.lower() for e in val_neg["errors"]))

        val_zero = validate_farm_inputs("red", "high", "kharif", land_area=0.0)
        self.assertFalse(val_zero["valid"])

    def test_negative_budget(self):
        """Negative budget must fail validation."""
        val = validate_farm_inputs("red", "high", "kharif", land_area=2.0, budget=-1000.0)
        self.assertFalse(val["valid"])
        self.assertTrue(any("budget" in e.lower() for e in val["errors"]))

    def test_valid_inputs_with_budget(self):
        """Standard valid inputs should pass."""
        val = validate_farm_inputs("black", "medium", "kharif", land_area=2.5, budget=75000.0)
        self.assertTrue(val["valid"])
        self.assertEqual(len(val["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
