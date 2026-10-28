from app.tools.rag_tool import (
    rag_search_tool
)


queries = [
    "What soil is suitable for tomato?",
    "What soil is suitable for groundnut?",
    "When is chilli cultivated?",
    "What should I consider when growing paddy?"
]


for query in queries:

    print("\n")
    print("=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    results = rag_search_tool(
        query=query,
        top_k=3
    )

    for result in results:

        print("\n----------------------------------------")
        print("Crop:", result.get("crop"))
        print("Source ID:", result.get("source_id"))
        print("Organization:", result.get("organization"))
        print("Title:", result.get("title"))
        print("Topic:", result.get("topic"))
        print("Document:", result.get("source"))
        print("Distance:", round(result.get("distance", 0), 4))
        print("Text:", result.get("text", "")[:300])
