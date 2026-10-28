import re


def normalize_text(value):
    return str(value or "").strip().lower()


def extract_numbers(text):
    """Extract numbers such as 2500, 2,500 and 25.50."""
    pattern = r"(?<!\w)-?\d+(?:,\d{3})*(?:\.\d+)?"

    numbers = []

    for value in re.findall(pattern, text or ""):
        try:
            numbers.append(float(value.replace(",", "")))
        except ValueError:
            continue

    return numbers


def number_is_present(answer, expected, tolerance=0.01):
    return any(
        abs(number - float(expected)) <= tolerance
        for number in extract_numbers(answer)
    )


def check_recommendation(answer, ranking):
    """Check whether the answer mentions the ranked crop."""
    crop = ranking.get("recommended_crop")

    if not crop:
        ranked = ranking.get("ranked_crops", [])

        if ranked and isinstance(ranked[0], dict):
            crop = ranked[0].get("crop")

    if not crop:
        return {
            "passed": False,
            "reason": "No deterministic recommendation was found."
        }

    return {
        "passed": normalize_text(crop) in normalize_text(answer),
        "expected_crop": crop
    }


def check_financial_value(answer, label, expected_value):
    """
    Check a value only when the answer explicitly reports it.
    A missing value is not automatically a failure because
    the LLM may choose not to include every tool result.
    """
    if expected_value is None:
        return {
            "passed": True,
            "status": "unavailable"
        }

    answer_lower = normalize_text(answer)

    if label not in answer_lower:
        return {
            "passed": True,
            "status": "not_reported"
        }

    return {
        "passed": number_is_present(answer, expected_value),
        "status": "checked",
        "expected_value": expected_value
    }


def check_citations(citations):
    """Check basic citation metadata completeness."""
    if not isinstance(citations, list):
        return {
            "passed": False,
            "reason": "Citations must be a list."
        }

    invalid = []

    for index, citation in enumerate(citations):
        if not isinstance(citation, dict):
            invalid.append(index)
            continue

        if not citation.get("title") and not citation.get("source_id"):
            invalid.append(index)

    return {
        "passed": len(invalid) == 0,
        "citation_count": len(citations),
        "invalid_indices": invalid
    }


def check_market_data_status(tool_results):
    """
    Inspect market tool results and flag unavailable data.
    Supports the common {tool, result} wrapper structure.
    """
    unavailable = []

    for item in tool_results:
        if not isinstance(item, dict):
            continue

        tool_name = normalize_text(item.get("tool", ""))

        if "market" not in tool_name:
            continue

        result = item.get("result", {})

        if not isinstance(result, dict):
            continue

        status = normalize_text(result.get("status", ""))

        current = result.get("current", {})
        if isinstance(current, dict):
            current_status = normalize_text(
                current.get("status", "")
            )
        else:
            current_status = ""

        if "unavailable" in (status, current_status):
            unavailable.append({
                "tool": tool_name,
                "status": status or current_status
            })

    return {
        "passed": len(unavailable) == 0,
        "unavailable_market_results": unavailable
    }


def evaluate_consistency(
    answer,
    ranking,
    tool_results,
    citations
):
    recommendation = check_recommendation(answer, ranking)
    citation_check = check_citations(citations)
    market_check = check_market_data_status(tool_results)

    checks = {
        "recommendation_matches_ranking": recommendation,
        "citation_metadata_valid": citation_check,
        "market_data_available": market_check
    }

    return {
        "passed": all(
            item.get("passed", False)
            for item in checks.values()
        ),
        "checks": checks
    }
