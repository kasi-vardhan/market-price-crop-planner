from app.rag.crop_detection import (
    detect_crop
)


questions = [
    "What soil is suitable for tomato?",
    "How much water does chilli need?",
    "Tell me about groundnut cultivation",
    "What are the requirements for paddy?"
]


for question in questions:

    crop = detect_crop(
        question
    )

    print(
        f"{question} -> {crop}"
    )
