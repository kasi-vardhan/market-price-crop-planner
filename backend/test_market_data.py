from app.services.market_intelligence import analyze_market


result = analyze_market(
    "chilli"
)


print("\n==============================")
print("MARKET DATA")
print("==============================")


print(
    "\nCrop:",
    result["crop"]
)

print(
    "Market:",
    result["market"]
)

print(
    "Location:",
    result["location"]
)

print(
    "Date:",
    result["date"]
)

print(
    "Source:",
    result["source"]
)

print(
    "Current Price:",
    result["current_price"]
)

print(
    "Trend:",
    result["trend"]
)

print(
    "Outlook:",
    result["outlook"]
)
