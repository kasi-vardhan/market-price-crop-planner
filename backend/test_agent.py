from app.agents.agriculture_agent import run_agriculture_agent


result = run_agriculture_agent(

    farmer_question="""
    I have 2 acres of red soil near Markapur.
    I have medium water availability.
    Which crop should I consider?
    """,

    location="markapur",

    soil="red",

    water="medium",

    season="kharif",

    land_area=2
)


print("\n================================")
print("AGRICULTURE AGENT RESULT")
print("================================")

print("\nRecommended Crop:")
print(result["recommended_crop"])


print("\nWeather:")
print(result["weather"])


print("\nCrop Analysis:")

for crop in result["crop_analysis"]:

    print("\nCrop:", crop["crop"])

    print(
        "Suitability Score:",
        crop["suitability"]["score"]
    )

    print(
        "Suitability Level:",
        crop["suitability"]["level"]
    )

    print(
        "Market:",
        crop["market"]["market"]
    )

    print(
        "Current Price:",
        crop["market"]["current_price"]
    )

    print(
        "Trend:",
        crop["market"]["trend"]
    )

    print(
        "Profit:",
        crop["profit"]["profit"]
    )


print("\nKnowledge Sources:")

for item in result["knowledge"]:

    print(
        item["source"]
    )
