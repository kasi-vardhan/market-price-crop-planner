from app.rag.retriever import search_knowledge


queries = [
    "What soil is suitable for groundnut?",
    "When is chilli cultivated?",
    "What are important factors for tomato cultivation?",
    "What factors affect paddy crop planning?"
]


for query in queries:

    print("\n================================")
    print("QUERY:", query)
    print("================================")

    results = search_knowledge(
        query=query,
        top_k=3
    )

    for result in results:

        print(
            "\nSOURCE:",
            result["source"],
            "| CROP:",
            result.get("crop"),
            "| CATEGORY:",
            result.get("category")
        )

        print(
            result["text"][:500]
        )
