import unittest


def calculate_financials(
    yield_per_acre,
    price_per_unit,
    cost_per_acre,
    land_area,
):
    # Missing price means revenue and profit cannot be calculated.
    if price_per_unit is None:
        return {
            "revenue": None,
            "total_cost": cost_per_acre * land_area,
            "profit": None,
            "status": "unavailable",
        }

    revenue = yield_per_acre * price_per_unit * land_area
    total_cost = cost_per_acre * land_area

    return {
        "revenue": revenue,
        "total_cost": total_cost,
        "profit": revenue - total_cost,
        "status": "calculated",
    }


class TestFinancialEdgeCases(unittest.TestCase):
    def test_missing_price_does_not_create_profit(self):
        result = calculate_financials(
            yield_per_acre=100,
            price_per_unit=None,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertIsNone(result["revenue"])
        self.assertIsNone(result["profit"])
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["status"], "unavailable")

    def test_negative_profit_is_preserved(self):
        result = calculate_financials(
            yield_per_acre=10,
            price_per_unit=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["revenue"], 400)
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["profit"], -600)
        self.assertEqual(result["status"], "calculated")


if __name__ == "__main__":
    unittest.main()
