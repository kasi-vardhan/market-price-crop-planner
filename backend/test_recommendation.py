from app.services.crop_recommendation import rank_crops


crop_analysis = [
    {
        "crop": "tomato",

        "suitability": {
            "score": 90,
            "level": "high"
        },

        "market": {
            "outlook": "positive",
            "historical_prices": [
                22, 23, 21, 24, 25, 26, 25
            ]
        },

        "profit": {
            "profit": 120000
        }
    }, 

    {
        "crop": "chilli",

        "suitability": {
            "score": 80,
            "level": "high"
        },

        "market": {
            "outlook": "positive",
            "historical_prices": [
                105, 108, 110, 115, 118, 120, 120
            ]
        },

        "profit": {
            "profit": 150000
        }
    },

    {
        "crop": "groundnut",

        "suitability": {
            "score": 75,
            "level": "medium"
        },

        "market": {
            "outlook": "stable",
            "historical_prices": [
                65, 66, 64, 67, 69, 70, 70
            ]
        },

        "profit": {
            "profit": 90000
        }
    }
]


result = rank_crops(crop_analysis)


print("\nRecommended Crop:")
print(result["recommended_crop"])

print("\nRecommendation Score:")
print(result["recommendation_score"])

print("\nRanked Crops:")

for crop in result["ranked_crops"]:

    print(
        crop["rank"],
        crop["crop"],
        crop["overall_score"]
    )

    print(
        crop["component_scores"]
    )

    print()
