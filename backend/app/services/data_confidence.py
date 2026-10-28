def get_source_score(status):
    """
    Convert data availability status into
    a confidence score.
    """

    status = str(status).lower().strip()

    if status == "live":
        return 100

    if status == "cached":
        return 60

    if status == "available":
        return 100

    if status == "unavailable":
        return 0

    return 30


def calculate_knowledge_score(
    source_count
):

    if source_count >= 3:
        return 100

    if source_count == 2:
        return 85

    if source_count == 1:
        return 70

    return 0


def calculate_data_confidence(
    weather_status,
    climate_status,
    market_statuses,
    has_profit_data,
    has_suitability_data,
    knowledge_source_count
):
    scores = []

    scores.append(
        get_source_score(
            weather_status
        )
    )

    scores.append(
        get_source_score(
            climate_status
        )
    )

    if market_statuses:

        market_scores = [
            get_source_score(status)
            for status in market_statuses
        ]

        scores.append(
            sum(market_scores)
            / len(market_scores)
        )

    else:

        scores.append(0)

    scores.append(
        100 if has_profit_data else 0
    )

    scores.append(
        100 if has_suitability_data else 0
    )

    scores.append(
        calculate_knowledge_score(
            knowledge_source_count
        )
    )

    overall_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    overall_score = round(
        overall_score,
        2
    )

    if overall_score >= 80:

        level = "high"

    elif overall_score >= 60:

        level = "medium"

    else:

        level = "low"

    return {
        "score": overall_score,
        "level": level,
        "explanation": (
            "Confidence reflects the availability "
            "and quality of the data used by the "
            "planning system. It is not a guarantee "
            "that the recommendation will be correct."
        )
    }
