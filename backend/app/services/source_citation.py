def build_source_citations(
    knowledge_results
):
    """
    Build a clean, deduplicated list of
    sources used by the RAG system.
    """

    if not knowledge_results:
        return []

    citations = []

    seen = set()

    for item in knowledge_results:

        if not isinstance(item, dict):
            continue

        source_id = item.get(
            "source_id"
        )

        title = item.get(
            "title"
        )

        organization = item.get(
            "organization"
        )

        url = item.get(
            "url"
        )

        source = item.get(
            "source"
        )

        crop = item.get(
            "crop"
        )

        topic = item.get(
            "topic"
        )

        passage = item.get(
            "text"
        ) or item.get("passage")

        # Must have a valid title and URL (never general homepage)
        if not url or url.rstrip("/") == "https://icar.gov.in" or not title:
            continue

        # Prefer source_id or title for deduplication.
        unique_key = (
            f"{source_id}_{title}"
            if source_id
            else (title or source)
        )

        if not unique_key:
            continue

        if unique_key in seen:
            continue

        seen.add(
            unique_key
        )

        citations.append(
            {
                "source_id": source_id,
                "title": title,
                "organization": organization,
                "url": url,
                "document": source,
                "crop": crop,
                "topic": topic,
                "passage": passage.strip() if isinstance(passage, str) else None
            }
        )

    return citations
