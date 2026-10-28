from app.services.llm_service import generate_crop_explanation


crop_data = {
    "crop": "chilli",
    "suitability_score": 100,
    "suitability_level": "high",
    "market": "Guntur",
    "expected_price": 120,
    "trend": "rising",
    "outlook": "positive",
    "revenue": 600000,
    "cost": 70000,
    "profit": 530000
}


question = """
I have red soil, medium water availability,
and I am considering chilli. Is it suitable?
"""


answer = generate_crop_explanation(
    crop_data=crop_data,
    farmer_question=question
)


print(answer)
