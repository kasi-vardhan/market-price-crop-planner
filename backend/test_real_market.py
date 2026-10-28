from app.services.real_market_repository import get_real_market_prices

result = get_real_market_prices(
    state="Andhra Pradesh",
    commodity="Chilli"
)

print("\n==============================")
print("REAL MARKET DATA")
print("==============================")

if "error" in result:
    print("ERROR:", result["error"])
else:
    print("Records:", result["count"])
    for record in result["records"][:10]:
        print("\n-------------------------")
        print("Crop:", record["crop"])
        print("Market:", record["market"])
        print("District:", record["location"])
        print("Date:", record["date"])
        print("Min:", record["min_price"])
        print("Max:", record["max_price"])
        print("Modal:", record["modal_price"])
