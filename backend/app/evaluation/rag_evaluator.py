import json
import math
from pathlib import Path

from app.rag.retriever import search_knowledge


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_CASE_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "rag"
    / "rag_test_cases.json"
)

RESULT_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "rag"
    / "results.json"
)


def load_test_cases():
    with open(TEST_CASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def calculate_keyword_score(expected_keywords, retrieved_results):
    if not expected_keywords:
        return 1.0

    combined_text = " ".join(
        normalize(item.get("text", ""))
        for item in retrieved_results
    )

    matched = 0

    for keyword in expected_keywords:
        if normalize(keyword) in combined_text:
            matched += 1

    return matched / len(expected_keywords)


def calculate_crop_correctness(expected_crop, retrieved_results):
    if expected_crop is None:
        return True

    expected_crop = normalize(expected_crop)

    for item in retrieved_results:
        retrieved_crop = normalize(item.get("crop"))

        if retrieved_crop == expected_crop:
            return True

    return False


def calculate_topic_score(expected_topics, retrieved_results):
    if not expected_topics:
        return 1.0

    retrieved_topics = {
        normalize(item.get("topic"))
        for item in retrieved_results
    }

    matched = sum(
        1
        for topic in expected_topics
        if normalize(topic) in retrieved_topics
    )

    return matched / len(expected_topics)


def calculate_source_hit(expected_sources, retrieved_results):
    if not expected_sources:
        return False

    retrieved_sources = {
        normalize(item.get("source_id"))
        for item in retrieved_results
    }

    for source_id in expected_sources:
        if normalize(source_id) in retrieved_sources:
            return True

    return False


def calculate_precision_at_k(expected_sources, retrieved_results):
    if not retrieved_results:
        return 0.0

    expected_sources = {
        normalize(source)
        for source in expected_sources
    }

    relevant = 0

    for item in retrieved_results:
        source_id = normalize(item.get("source_id"))

        if source_id in expected_sources:
            relevant += 1

    return relevant / len(retrieved_results)


def calculate_mrr(expected_sources, retrieved_results):
    if not expected_sources:
        return 0.0

    expected_sources = {
        normalize(source)
        for source in expected_sources
    }

    for index, item in enumerate(retrieved_results, start=1):
        source_id = normalize(item.get("source_id"))

        if source_id in expected_sources:
            return 1.0 / index

    return 0.0


def calculate_average_distance(retrieved_results):
    distances = []

    for item in retrieved_results:
        distance = item.get("distance")

        if isinstance(distance, (int, float)):
            if math.isfinite(distance):
                distances.append(distance)

    if not distances:
        return None

    return round(sum(distances) / len(distances), 4)


def evaluate_case(test_case, top_k=3):
    query = test_case["query"]
    expected_crop = test_case.get("expected_crop")
    expected_topics = test_case.get("expected_topics", [])
    expected_sources = test_case.get("expected_source_ids", [])
    expected_keywords = test_case.get("expected_keywords", [])

    retrieved_results = search_knowledge(
        query=query,
        crop=expected_crop,
        top_k=top_k
    )

    crop_correct = calculate_crop_correctness(
        expected_crop,
        retrieved_results
    )

    source_hit = calculate_source_hit(
        expected_sources,
        retrieved_results
    )

    topic_score = calculate_topic_score(
        expected_topics,
        retrieved_results
    )

    keyword_score = calculate_keyword_score(
        expected_keywords,
        retrieved_results
    )

    precision_at_k = calculate_precision_at_k(
        expected_sources,
        retrieved_results
    )

    mrr = calculate_mrr(
        expected_sources,
        retrieved_results
    )

    return {
        "id": test_case["id"],
        "query": query,
        "expected_crop": expected_crop,
        "expected_topics": expected_topics,
        "expected_source_ids": expected_sources,
        "retrieved": [
            {
                "source_id": item.get("source_id"),
                "source": item.get("source"),
                "organization": item.get("organization"),
                "title": item.get("title"),
                "crop": item.get("crop"),
                "topic": item.get("topic"),
                "distance": item.get("distance")
            }
            for item in retrieved_results
        ],
        "metrics": {
            "crop_correct": crop_correct,
            "source_hit": source_hit,
            "topic_score": round(topic_score, 4),
            "keyword_score": round(keyword_score, 4),
            "precision_at_k": round(precision_at_k, 4),
            "mrr": round(mrr, 4),
            "average_distance": calculate_average_distance(
                retrieved_results
            )
        }
    }


def calculate_aggregate(results):
    if not results:
        return {}

    total = len(results)

    crop_accuracy = sum(
        1
        for result in results
        if result["metrics"]["crop_correct"]
    ) / total

    source_hit_rate = sum(
        1
        for result in results
        if result["metrics"]["source_hit"]
    ) / total

    topic_hit_rate = sum(
        result["metrics"]["topic_score"]
        for result in results
    ) / total

    keyword_score = sum(
        result["metrics"]["keyword_score"]
        for result in results
    ) / total

    precision_at_k = sum(
        result["metrics"]["precision_at_k"]
        for result in results
    ) / total

    mrr = sum(
        result["metrics"]["mrr"]
        for result in results
    ) / total

    distances = [
        result["metrics"]["average_distance"]
        for result in results
        if result["metrics"]["average_distance"] is not None
    ]

    average_distance = (
        sum(distances) / len(distances)
        if distances
        else None
    )

    return {
        "total_test_cases": total,
        "crop_accuracy": round(crop_accuracy, 4),
        "source_hit_rate": round(source_hit_rate, 4),
        "topic_hit_rate": round(topic_hit_rate, 4),
        "keyword_score": round(keyword_score, 4),
        "precision_at_k": round(precision_at_k, 4),
        "mrr": round(mrr, 4),
        "average_retrieval_distance": (
            round(average_distance, 4)
            if average_distance is not None
            else None
        )
    }


def run_evaluation():
    test_cases = load_test_cases()

    results = []

    for test_case in test_cases:
        print(f"Evaluating {test_case['id']}...")

        result = evaluate_case(
            test_case=test_case,
            top_k=3
        )

        results.append(result)

    aggregate = calculate_aggregate(results)

    report = {
        "evaluation": "RAG Retrieval Evaluation",
        "top_k": 3,
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

    print("\n===== RAG EVALUATION =====")

    for key, value in report["aggregate"].items():
        print(f"{key}: {value}")

    print(
        f"\nDetailed results saved to:\n{RESULT_PATH}"
    )
