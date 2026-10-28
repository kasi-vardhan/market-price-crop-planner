import json
from pathlib import Path


HISTORY_FILE = Path(
    "../data/market_history/market_history.json"
) if Path("../data/market_history/market_history.json").exists() else Path(
    "data/market_history/market_history.json"
)


def load_history():
    """
    Load previously stored market observations.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    return []


def save_history(records):
    """
    Save market observations to disk.
    """

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )


def add_market_records(records):
    """
    Add new market observations while avoiding
    exact duplicates.
    """

    history = load_history()

    existing_keys = {
        (
            item.get("crop"),
            item.get("market"),
            item.get("date"),
            item.get("modal_price")
        )
        for item in history
    }

    added = 0

    for record in records:

        key = (
            record.get("crop"),
            record.get("market"),
            record.get("date"),
            record.get("modal_price")
        )

        if key in existing_keys:
            continue

        history.append(record)
        existing_keys.add(key)
        added += 1

    save_history(history)

    return {
        "added": added,
        "total": len(history)
    }
