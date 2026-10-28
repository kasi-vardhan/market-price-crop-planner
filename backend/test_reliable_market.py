from app.services.reliable_market_service import (
    get_reliable_market_price
)


result = get_reliable_market_price(
    crop="chilli"
)


print("\n================================")
print("RELIABLE MARKET SERVICE")
print("================================")


print(
    "\nStatus:",
    result["status"]
)

print(
    "Source:",
    result["source"]
)

if result.get("cached_at"):

    print(
        "Cached At:",
        result["cached_at"]
    )


print("\nRecords:")

records = result.get("records") or ([result] if "crop" in result else [])

for record in records:

    print("\n--------------------")

    print(
        "Crop:",
        record["crop"]
    )

    print(
        "Market:",
        record["market"]
    )

    print(
        "Min:",
        record["min_price"]
    )

    print(
        "Modal:",
        record["modal_price"]
    )

    print(
        "Max:",
        record["max_price"]
    )
