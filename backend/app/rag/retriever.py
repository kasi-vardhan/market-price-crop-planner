import pickle
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
INDEX_PATH = str(BASE_DIR / "knowledge_base" / "processed" / "index.faiss")
METADATA_PATH = str(BASE_DIR / "knowledge_base" / "processed" / "metadata.pkl")

MODEL_NAME = "all-MiniLM-L6-v2"


embedding_model = SentenceTransformer(
    MODEL_NAME
)


def load_index_and_metadata():
    if not Path(INDEX_PATH).exists() or not Path(METADATA_PATH).exists():
        return None, []
    
    idx = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        meta = pickle.load(f)
    return idx, meta


def rerank_results(
    results,
    crop=None
):

    if not crop:
        return results

    crop = crop.lower()

    for item in results:

        if item.get("crop") == crop:

            item["rerank_score"] = (
                item["distance"] - 0.15
            )

        else:

            item["rerank_score"] = (
                item["distance"]
            )

    return sorted(
        results,
        key=lambda item:
            item["rerank_score"]
    )


def search_knowledge(
    query: str,
    top_k: int = 3,
    crop: str | None = None
):
    idx, metadata = load_index_and_metadata()
    if idx is None or not metadata:
        return []

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = idx.search(
        query_embedding,
        min(
            top_k * 5,
            len(metadata)
        )
    )

    results = []

    crop = (
        crop.lower().strip()
        if crop
        else None
    )

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):

        if index_id < 0:
            continue

        item = metadata[index_id]

        if crop:

            item_crop = str(
                item.get("crop", "")
            ).lower()

            if (
                item_crop != crop
                and item_crop != "general"
            ):
                continue

        results.append(
            {
                "chunk_id": item.get(
                    "chunk_id"
                ),

                "source_id": item.get(
                    "source_id"
                ),

                "source": item.get(
                    "source"
                ),

                "organization": item.get(
                    "organization"
                ),

                "title": item.get(
                    "title"
                ),

                "document_type": item.get(
                    "document_type"
                ),

                "url": item.get(
                    "url"
                ),

                "crop": item.get(
                    "crop"
                ),

                "topic": item.get(
                    "topic"
                ),

                "text": item.get(
                    "text"
                ),

                "distance": float(
                    distance
                )
            }
        )

        if len(results) >= top_k:
            break

    results = rerank_results(
        results,
        crop=crop
    )

    return results[:top_k]
