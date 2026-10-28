import requests
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

scenarios = [
    {
        "title": "Scenario 1: Red Soil + High Water (Markapur - Kharif)",
        "payload": {
            "farmer_question": "What crop should I grow with good water on red soil?",
            "location": "Markapur",
            "soil": "red",
            "water": "high",
            "season": "kharif",
            "land_area": 2.0
        }
    },
    {
        "title": "Scenario 2: Red Soil + Medium Water (Markapur - Rabi)",
        "payload": {
            "farmer_question": "Which crop is best for rabi season with medium water?",
            "location": "Markapur",
            "soil": "red",
            "water": "medium",
            "season": "rabi",
            "land_area": 3.0
        }
    },
    {
        "title": "Scenario 3: Clay Soil + High Water (Ongole - Kharif)",
        "payload": {
            "farmer_question": "I have heavy clay soil and plenty of canal water for kharif.",
            "location": "Ongole",
            "soil": "clay",
            "water": "high",
            "season": "kharif",
            "land_area": 5.0
        }
    }
]

for s in scenarios:
    print("=" * 60)
    print(s["title"])
    print("=" * 60)
    try:
        res = requests.post("http://127.0.0.1:8000/api/plan", json=s["payload"], timeout=90)
        print("HTTP Status:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            print("  Recommended Crop :", str(data.get("recommended_crop")).capitalize())
            print("  Recommendation Score :", f"{data.get('recommendation_score', 0):.1f}%")
            w = data.get("weather", {})
            print("  Live Weather     :", f"{w.get('temperature')}°C | Status: {w.get('status')} | Source: {w.get('source')}")
            
            top_profit = next(
                (p for p in data.get("profit_analysis", []) if str(p.get("crop")).lower() == str(data.get("recommended_crop")).lower()),
                data.get("profit_analysis", [{}])[0] if data.get("profit_analysis") else {}
            )
            print("  Estimated Profit :", f"₹{top_profit.get('profit', 0):,.0f}" if top_profit.get("profit") is not None else "Unavailable")
            print("  Data Confidence  :", data.get("data_confidence", {}).get("level", "N/A").capitalize())
            print("  Sources Cited    :", len(data.get("sources", [])))
        else:
            print("  Error:", res.text)
    except Exception as e:
        print("  Request Failed:", e)
    print()
