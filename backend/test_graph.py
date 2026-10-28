from app.agents.agriculture_graph import agriculture_graph


initial_state = {

    "farmer_question": """
    I have 2 acres of red soil near Markapur.
    I have medium water availability.
    Which crop should I consider?
    """,

    "location": "markapur",

    "soil": "red",

    "water": "medium",

    "season": "kharif",

    "land_area": 2
}


result = agriculture_graph.invoke(
    initial_state
)


print("\n================================")
print("LANGGRAPH RESULT")
print("================================")


print("\nRecommended Crop:")
print(result.get("recommended_crop"))


print("\nWeather:")
print(result.get("weather"))


print("\nCrop Analysis:")
for item in result.get("crop_analysis", []):
    print("\nCrop:", item["crop"])
    print("Suitability:", item["suitability"]["score"])
    print("Profit:", item["profit"]["profit"])


print("\nKnowledge:")
for item in result.get("knowledge", []):
    print(item["source"])
