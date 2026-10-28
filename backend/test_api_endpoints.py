"""
API integration tests for FastAPI application using TestClient.
Tests:
- GET / and GET /health
- POST /api/plan with valid inputs + budget
- POST /api/plan with invalid land area (negative check) -> 422 / 400 validation error
- POST /api/plan with invalid soil -> 400 / 422 validation error
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_and_health(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("running", res.json()["message"])

        res_h = self.client.get("/health")
        self.assertEqual(res_h.status_code, 200)
        self.assertEqual(res_h.json()["status"], "healthy")

    def test_plan_api_invalid_inputs(self):
        # Negative land area triggers validation error (HTTP 422 or 400)
        payload = {
            "location": "Markapur",
            "soil": "red",
            "water": "high",
            "season": "kharif",
            "land_area": -2.0,
            "budget": 50000.0,
        }
        res = self.client.post("/api/plan", json=payload)
        self.assertIn(res.status_code, [400, 422])

        # Invalid soil triggers validation error
        payload_soil = {
            "location": "Markapur",
            "soil": "moon_rock",
            "water": "high",
            "season": "kharif",
            "land_area": 2.0,
        }
        res = self.client.post("/api/plan", json=payload_soil)
        self.assertIn(res.status_code, [400, 422])

    def test_plan_api_valid_request(self):
        payload = {
            "farmer_question": "What is the best crop for low investment?",
            "location": "Markapur",
            "soil": "red",
            "water": "high",
            "season": "kharif",
            "land_area": 2.0,
            "budget": 60000.0,
        }
        res = self.client.post("/api/plan", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("recommended_crop", data)
        self.assertIn("recommendation_score", data)
        self.assertIn("recommendation", data)
        self.assertIn("ranking", data)
        self.assertIn("crop_suitability", data)
        self.assertIn("profit_analysis", data)
        self.assertIn("weather", data)
        self.assertIn("climate", data)

        # Verify ranking contains ranked_crops
        ranking = data["ranking"]
        self.assertIn("ranked_crops", ranking)
        self.assertGreaterEqual(len(ranking["ranked_crops"]), 3)

        # Verify budget was respected
        top_crop = ranking["ranked_crops"][0]
        self.assertFalse(top_crop.get("budget_exceeded", False))


if __name__ == "__main__":
    unittest.main()
