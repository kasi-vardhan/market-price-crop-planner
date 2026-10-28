from app.services.crop_suitability import (
    calculate_suitability
)


crops = [
    "tomato",
    "chilli",
    "groundnut",
    "paddy"
]


for crop in crops:

    result = calculate_suitability(
        crop_name=crop,
        soil="red",
        water="high",
        season="kharif",
        temperature=27,
        rainfall=900
    )

    print("\n-----------------------")
    print(crop)
    print("-----------------------")

    print(
        "Score:",
        result["score"]
    )

    print(
        "Level:",
        result["level"]
    )

    print(
        "Components:",
        result["component_scores"]
    )

    print(
        "Reasons:"
    )

    for reason in result["reasons"]:
        print(
            "-",
            reason
        )
