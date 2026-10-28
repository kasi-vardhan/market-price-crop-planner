from app.services.real_market_repository import (
    get_real_market_prices
)

from app.services.market_history_repository import (
    add_market_records
)


DEFAULT_COMMODITIES = [
    "Tomato",
    "Chilli",
    "Groundnut",
    "Paddy"
]


def collect_market_history(
    state="Andhra Pradesh",
    commodities=None
):
    """
    Collect live market observations and store them
    in the local historical dataset.
    """

    if commodities is None:
        commodities = DEFAULT_COMMODITIES

    total_added = 0
    total_records = 0
    results = []

    for commodity in commodities:

        response = get_real_market_prices(
            state=state,
            commodity=commodity
        )

        if response.get("status") != "live":

            results.append({
                "commodity": commodity,
                "status": "unavailable",
                "error": response.get(
                    "error",
                    "Market data unavailable."
                )
            })

            continue

        records = response.get(
            "records",
            []
        )

        if not records:

            results.append({
                "commodity": commodity,
                "status": "unavailable",
                "error": (
                    "No records returned."
                )
            })

            continue

        storage_result = add_market_records(
            records
        )

        added = storage_result.get(
            "added",
            0
        )

        total_added += added
        total_records += len(records)

        results.append({
            "commodity": commodity,
            "status": "success",
            "records_received": len(records),
            "records_added": added
        })

    return {
        "status": "completed",
        "state": state,
        "commodities": commodities,
        "records_received": total_records,
        "records_added": total_added,
        "results": results
    }
