from datetime import datetime


DATE_FORMATS = [
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%y"
]


def parse_market_date(value):

    if not value:
        return None

    value = str(value).strip()

    for date_format in DATE_FORMATS:

        try:

            return datetime.strptime(
                value,
                date_format
            ).date()

        except ValueError:
            continue

    return None
