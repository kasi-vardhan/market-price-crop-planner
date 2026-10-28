def to_float(value):

    if value is None:
        return None

    if isinstance(
        value,
        (int, float)
    ):
        return float(value)

    try:

        cleaned = str(
            value
        ).replace(
            ",",
            ""
        ).strip()

        if not cleaned:
            return None

        return float(cleaned)

    except (
        TypeError,
        ValueError
    ):

        return None


def normalize_market_record(
    record: dict
):
    """
    Convert an OGD market record into the
    application's internal format.

    Missing numeric values are preserved as None.
    """

    crop = record.get(
        "commodity"
    )

    market = record.get(
        "market"
    )

    district = record.get(
        "district"
    )

    state = record.get(
        "state"
    )

    arrival_date = record.get(
        "arrival_date"
    )

    min_price = to_float(
        record.get(
            "min_price"
        )
    )

    max_price = to_float(
        record.get(
            "max_price"
        )
    )

    modal_price = to_float(
        record.get(
            "modal_price"
        )
    )

    return {
        "crop": crop,
        "market": market,
        "location": district,
        "state": state,
        "date": arrival_date,

        "min_price": min_price,
        "max_price": max_price,
        "modal_price": modal_price,

        "source": (
            "Government of India OGD"
        )
    }
