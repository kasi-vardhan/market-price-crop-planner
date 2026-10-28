from app.services.market_api import (
    fetch_market_data
)

from app.services.market_normalizer import (
    normalize_market_record
)


def get_real_market_prices(
    state="Andhra Pradesh",
    commodity=None
):
    """
    Retrieve and normalize live OGD market data.
    """

    response = fetch_market_data(
        state=state,
        commodity=commodity
    )

    if response.get(
        "status"
    ) != "live":

        return response

    records = response.get(
        "records",
        []
    )

    normalized_records = []

    for record in records:

        if not isinstance(
            record,
            dict
        ):
            continue

        normalized = normalize_market_record(
            record
        )

        # A market record is usable only if
        # the essential fields are available.

        if not normalized.get(
            "crop"
        ):
            continue

        if not normalized.get(
            "market"
        ):
            continue

        if normalized.get(
            "modal_price"
        ) is None:
            continue

        normalized_records.append(
            normalized
        )

    if not normalized_records:

        return {
            "status": "unavailable",
            "source": (
                "Government of India OGD"
            ),
            "error": (
                "No usable market records "
                "were returned."
            )
        }

    return {
        "status": "live",
        "source": (
            "Government of India OGD"
        ),
        "count": len(
            normalized_records
        ),
        "records": normalized_records
    }
