def compare_markets(records):
    """
    Compare available mandi records using modal price.
    """

    valid_records = []

    for record in records:

        modal_price = record.get("modal_price")

        if not isinstance(
            modal_price,
            (int, float)
        ):
            continue

        valid_records.append(record)

    if not valid_records:
        return {
            "status": "unavailable",
            "markets": [],
            "best_market": None
        }

    sorted_markets = sorted(
        valid_records,
        key=lambda item: item["modal_price"],
        reverse=True
    )

    best_market = sorted_markets[0]

    return {
        "status": "available",
        "market_count": len(sorted_markets),
        "markets": sorted_markets,
        "best_market": best_market
    }
