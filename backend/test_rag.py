from app.rag.retriever import search_knowledge


results = search_knowledge(
    "What type of soil is suitable for chilli?"
)


for result in results:

    print("\nSOURCE:")
    print(result["source"])

    print("\nTEXT:")
    print(result["text"])
