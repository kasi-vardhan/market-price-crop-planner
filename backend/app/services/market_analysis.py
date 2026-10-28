def analyze_market_records(records):
    """
    Analyze current prices across multiple markets.
    """

    valid_records = [
        record
        for record in records
        if isinstance(
            record.get("modal_price"),
            (int, float)
        )
    ]

    if not valid_records:
        return {
            "status": "unavailable"
        }

    modal_prices = [
        record["modal_price"]
        for record in valid_records
    ]

    highest = max(modal_prices)
    lowest = min(modal_prices)

    average = sum(modal_prices) / len(
        modal_prices
    )

    highest_market = max(
        valid_records,
        key=lambda item: item["modal_price"]
    )

    lowest_market = min(
        valid_records,
        key=lambda item: item["modal_price"]
    )

    return {
        "status": "available",
        "highest_modal_price": highest,
        "lowest_modal_price": lowest,
        "average_modal_price": round(
            average,
            2
        ),
        "price_difference": round(
            highest - lowest,
            2
        ),
        "highest_price_market": highest_market,
        "lowest_price_market": lowest_market
    }
