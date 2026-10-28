import unittest

from app.tools.profit_tool import profit_calculator_tool


class TestProductionProfitTool(unittest.TestCase):
    def test_calculated_profit(self):
        result = profit_calculator_tool(
            crop="tomato",
            yield_per_acre=100,
            expected_price=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["revenue"], 4000)
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["profit"], 3000)
        self.assertEqual(result["status"], "calculated")

    def test_missing_price(self):
        result = profit_calculator_tool(
            crop="tomato",
            yield_per_acre=100,
            expected_price=None,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertIsNone(result["expected_price"])
        self.assertIsNone(result["revenue"])
        self.assertIsNone(result["profit"])
        self.assertEqual(result["total_cost"], 1000)
        self.assertEqual(result["status"], "unavailable")

    def test_loss_is_preserved(self):
        result = profit_calculator_tool(
            crop="tomato",
            yield_per_acre=10,
            expected_price=20,
            cost_per_acre=500,
            land_area=2,
        )

        self.assertEqual(result["profit"], -600)

    def test_invalid_land_area(self):
        with self.assertRaises(ValueError):
            profit_calculator_tool(
                crop="tomato",
                yield_per_acre=100,
                expected_price=20,
                cost_per_acre=500,
                land_area=0,
            )


if __name__ == "__main__":
    unittest.main()
