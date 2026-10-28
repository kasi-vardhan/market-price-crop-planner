import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_CASE_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "answer"
    / "answer_test_cases.json"
)

RESULT_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "answer"
    / "results.json"
)


def normalize_text(text):
    if text is None:
        return ""

    return str(text).strip().lower()


def contains_text(answer, expected):
    return normalize_text(expected) in normalize_text(answer)


def extract_numbers(text):
    """
    Extract numerical values from an answer.

    Handles:
    2500
    2,500
    25.5
    ₹25
    ₹2,500
    """

    if not text:
        return []

    pattern = r"(?<!\w)(?:₹\s*)?\d+(?:,\d{3})*(?:\.\d+)?"

    matches = re.findall(pattern, text)

    numbers = []

    for match in matches:
        cleaned = (
            match
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        try:
            numbers.append(float(cleaned))
        except ValueError:
            continue

    return numbers


def number_is_present(answer, expected_value, tolerance=0.01):
    numbers = extract_numbers(answer)

    for number in numbers:
        if abs(number - float(expected_value)) <= tolerance:
            return True

    return False


def validate_recommendation(answer, expected_crop):
    if not expected_crop:
        return True

    return contains_text(answer, expected_crop)


def validate_profit(answer, expected_profit):
    if expected_profit is None:
        return True

    return number_is_present(
        answer,
        expected_profit,
        tolerance=0.01
    )


def validate_revenue(answer, expected_revenue):
    if expected_revenue is None:
        return True

    return number_is_present(
        answer,
        expected_revenue,
        tolerance=0.01
    )


def validate_price(answer, expected_price):
    if expected_price is None:
        return True

    return number_is_present(
        answer,
        expected_price,
        tolerance=0.01
    )


def validate_sources(answer, expected_sources):
    """
    Verify that source titles or organizations supplied
    by the backend actually appear in the final answer.
    """

    if not expected_sources:
        return True

    answer_normalized = normalize_text(answer)

    matched = 0

    for source in expected_sources:
        source_title = normalize_text(
            source.get("title")
        )

        organization = normalize_text(
            source.get("organization")
        )

        if (
            source_title
            and source_title in answer_normalized
        ):
            matched += 1
            continue

        if (
            organization
            and organization in answer_normalized
        ):
            matched += 1

    return matched > 0


def evaluate_answer(test_case):
    answer = test_case["answer"]

    recommendation_ok = validate_recommendation(
        answer,
        test_case.get("recommended_crop")
    )

    profit_ok = validate_profit(
        answer,
        test_case.get("profit")
    )

    revenue_ok = validate_revenue(
        answer,
        test_case.get("revenue")
    )

    price_ok = validate_price(
        answer,
        test_case.get("expected_price")
    )

    sources_ok = validate_sources(
        answer,
        test_case.get("sources", [])
    )

    checks = {
        "recommendation_correct": recommendation_ok,
        "profit_correct": profit_ok,
        "revenue_correct": revenue_ok,
        "price_correct": price_ok,
        "sources_present": sources_ok
    }

    passed_checks = sum(
        1
        for value in checks.values()
        if value
    )

    total_checks = len(checks)

    grounding_score = (
        passed_checks / total_checks
        if total_checks
        else 0
    )

    return {
        "id": test_case["id"],
        "checks": checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "grounding_score": round(
            grounding_score,
            4
        )
    }


def run_evaluation():
    with open(
        TEST_CASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    results = []

    for test_case in test_cases:
        print(
            f"Evaluating answer {test_case['id']}..."
        )

        result = evaluate_answer(test_case)

        results.append(result)

    if results:
        average_grounding_score = (
            sum(
                result["grounding_score"]
                for result in results
            )
            / len(results)
        )
    else:
        average_grounding_score = 0

    aggregate = {
        "total_test_cases": len(results),
        "average_grounding_score": round(
            average_grounding_score,
            4
        ),
        "recommendation_accuracy": round(
            sum(
                result["checks"]["recommendation_correct"]
                for result in results
            ) / len(results),
            4
        ) if results else 0,
        "profit_accuracy": round(
            sum(
                result["checks"]["profit_correct"]
                for result in results
            ) / len(results),
            4
        ) if results else 0,
        "revenue_accuracy": round(
            sum(
                result["checks"]["revenue_correct"]
                for result in results
            ) / len(results),
            4
        ) if results else 0,
        "price_accuracy": round(
            sum(
                result["checks"]["price_correct"]
                for result in results
            ) / len(results),
            4
        ) if results else 0,
        "source_presence_rate": round(
            sum(
                result["checks"]["sources_present"]
                for result in results
            ) / len(results),
            4
        ) if results else 0
    }

    report = {
        "evaluation": "Final Answer Grounding Evaluation",
        "aggregate": aggregate,
        "cases": results
    }

    RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    return report


if __name__ == "__main__":
    report = run_evaluation()

    print("\n===== ANSWER GROUNDING EVALUATION =====")

    for key, value in report["aggregate"].items():
        print(f"{key}: {value}")

    print(
        f"\nDetailed results saved to:\n{RESULT_PATH}"
    )
