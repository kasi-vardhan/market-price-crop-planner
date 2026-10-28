import unittest

from app.tools.profit_tool import profit_calculator_tool


class TestProfitToolIntegration(unittest.TestCase):
    def test_profit_tool_returns_consistent_values(self):
        result = profit_calculator_tool(
            crop="tomato",
            yield_per_acre=100,
            expected_price=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["expected_yield"], 200)
        self.assertEqual(result["expected_price"], 20)
        self.assertEqual(result["revenue"], 4000)
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["profit"], 3000)

        self.assertAlmostEqual(
            result["profit"],
            result["revenue"] - result["total_cost"],
        )


if __name__ == "__main__":
    unittest.main()
