import unittest

from app.evaluation.consistency_checks import (
    check_recommendation,
    check_citations,
    check_market_data_status,
    number_is_present,
)


class TestConsistencyChecks(unittest.TestCase):

    def test_correct_recommendation(self):
        answer = "Recommended Crop: tomato"
        ranking = {"recommended_crop": "tomato"}

        result = check_recommendation(answer, ranking)

        self.assertTrue(result["passed"])

    def test_wrong_recommendation(self):
        answer = "Recommended Crop: chilli"
        ranking = {"recommended_crop": "tomato"}

        result = check_recommendation(answer, ranking)

        self.assertFalse(result["passed"])

    def test_financial_number_with_commas(self):
        answer = "Estimated profit: ₹45,000"

        self.assertTrue(
            number_is_present(answer, 45000)
        )

    def test_wrong_financial_number(self):
        answer = "Estimated profit: ₹50,000"

        self.assertFalse(
            number_is_present(answer, 45000)
        )

    def test_valid_citation(self):
        citations = [
            {
                "source_id": "tomato_icar",
                "title": "Agricultural Guidance"
            }
        ]

        result = check_citations(citations)

        self.assertTrue(result["passed"])

    def test_invalid_citation(self):
        citations = [{"url": "https://example.com"}]

        result = check_citations(citations)

        self.assertFalse(result["passed"])

    def test_unavailable_market(self):
        tool_results = [
            {
                "tool": "get_market_information",
                "result": {"status": "unavailable"}
            }
        ]

        result = check_market_data_status(tool_results)

        self.assertFalse(result["passed"])

    def test_live_market(self):
        tool_results = [
            {
                "tool": "get_market_information",
                "result": {"status": "live"}
            }
        ]

        result = check_market_data_status(tool_results)

        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
