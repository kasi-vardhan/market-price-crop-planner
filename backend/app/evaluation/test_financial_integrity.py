import unittest


def calculate_expected_financials(
    yield_per_acre,
    price_per_unit,
    cost_per_acre,
    land_area,
):
    revenue = yield_per_acre * price_per_unit * land_area
    total_cost = cost_per_acre * land_area
    profit = revenue - total_cost

    return {
        "revenue": revenue,
        "total_cost": total_cost,
        "profit": profit,
    }


class TestFinancialIntegrity(unittest.TestCase):
    def test_profit_matches_inputs(self):
        result = calculate_expected_financials(
            yield_per_acre=100,
            price_per_unit=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["revenue"], 4000)
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["profit"], 3000)

    def test_loss_is_negative_profit(self):
        result = calculate_expected_financials(
            yield_per_acre=10,
            price_per_unit=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["revenue"], 400)
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["profit"], -600)


if __name__ == "__main__":
    unittest.main()
