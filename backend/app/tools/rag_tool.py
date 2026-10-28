from app.rag.retriever import (
    search_knowledge
)

from app.rag.crop_detection import (
    detect_crop
)


def rag_search_tool(
    query: str,
    crop: str | None = None,
    top_k: int = 3
):

    if crop is None:

        crop = detect_crop(
            query
        )

    return search_knowledge(
        query=query,
        crop=crop,
        top_k=top_k
    )
