from app.services.market_history_repository import (
    add_market_records
)

from app.services.historical_market_analysis import (
    analyze_historical_market
)


sample_records = [
    {
        "crop": "tomato",
        "market": "Ongole",
        "location": "Prakasam",
        "state": "Andhra Pradesh",
        "date": "2026-10-01",
        "min_price": 20,
        "max_price": 30,
        "modal_price": 25,
        "source": "test"
    },
    {
        "crop": "tomato",
        "market": "Ongole",
        "location": "Prakasam",
        "state": "Andhra Pradesh",
        "date": "2026-10-02",
        "min_price": 21,
        "max_price": 31,
        "modal_price": 26,
        "source": "test"
    },
    {
        "crop": "tomato",
        "market": "Ongole",
        "location": "Prakasam",
        "state": "Andhra Pradesh",
        "date": "2026-10-03",
        "min_price": 22,
        "max_price": 32,
        "modal_price": 28,
        "source": "test"
    }
]


result = add_market_records(
    sample_records
)

print("Storage result:")
print(result)


analysis = analyze_historical_market(
    crop="tomato",
    market="Ongole",
    days=30
)

print("\nHistorical analysis:")
print(analysis)
