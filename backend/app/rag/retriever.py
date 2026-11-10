import pickle
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "knowledge_base" / "processed"
INDEX_PATH = PROCESSED_DIR / "index.faiss"
METADATA_PATH = PROCESSED_DIR / "metadata.pkl"
MODEL_PATH = PROCESSED_DIR / "minilm-transformer.onnx"
TOKENIZER_PATH = PROCESSED_DIR / "tokenizer.json"

MAX_SEQUENCE_LENGTH = 256


@lru_cache(maxsize=1)
def get_embedding_resources():
    """Load the lightweight ONNX model and tokenizer once."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ONNX model not found: {MODEL_PATH}")

    if not TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Tokenizer not found: {TOKENIZER_PATH}")

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )

    session = ort.InferenceSession(
        str(MODEL_PATH),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )

    tokenizer = Tokenizer.from_file(str(TOKENIZER_PATH))

    pad_id = tokenizer.token_to_id("[PAD]")
    if pad_id is None:
        raise ValueError("Tokenizer does not contain the [PAD] token")

    tokenizer.enable_truncation(max_length=MAX_SEQUENCE_LENGTH)
    tokenizer.enable_padding(
        pad_id=pad_id,
        pad_token="[PAD]",
    )

    return session, tokenizer


@lru_cache(maxsize=1)
def load_index_and_metadata():
    """Load and cache the FAISS index and its metadata."""

    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        return None, []

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "rb") as file:
        metadata = pickle.load(file)

    return index, metadata


def get_query_embedding(query: str) -> np.ndarray:
    """Generate a normalized MiniLM embedding using ONNX Runtime."""

    session, tokenizer = get_embedding_resources()

    encoding = tokenizer.encode(query)

    input_ids = np.asarray(
        [encoding.ids],
        dtype=np.int64,
    )

    attention_mask = np.asarray(
        [encoding.attention_mask],
        dtype=np.int64,
    )

    outputs = session.run(
        ["last_hidden_state"],
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        },
    )

    token_embeddings = outputs[0]

    mask = attention_mask.astype(np.float32)[..., None]

    summed_embeddings = np.sum(
        token_embeddings * mask,
        axis=1,
    )

    token_counts = np.maximum(
        np.sum(mask, axis=1),
        1e-9,
    )

    mean_embeddings = summed_embeddings / token_counts

    norms = np.linalg.norm(
        mean_embeddings,
        axis=1,
        keepdims=True,
    )

    normalized_embeddings = mean_embeddings / np.maximum(
        norms,
        1e-12,
    )

    return normalized_embeddings.astype(np.float32)


def rerank_results(results, crop=None):
    if not crop:
        return results

    crop = crop.lower()

    for item in results:
        if item.get("crop") == crop:
            item["rerank_score"] = item["distance"] - 0.15
        else:
            item["rerank_score"] = item["distance"]

    return sorted(
        results,
        key=lambda item: item["rerank_score"],
    )


def search_knowledge(
    query: str,
    top_k: int = 3,
    crop: str | None = None,
):
    index, metadata = load_index_and_metadata()

    if index is None or not metadata:
        return []

    query_embedding = get_query_embedding(query)

    search_count = min(
        max(1, top_k * 5),
        len(metadata),
    )

    distances, indices = index.search(
        query_embedding,
        search_count,
    )

    results = []
    crop = crop.lower().strip() if crop else None

    for distance, index_id in zip(distances[0], indices[0]):
        if index_id < 0:
            continue

        item = metadata[index_id]

        if crop:
            item_crop = str(item.get("crop", "")).lower()

            if item_crop != crop and item_crop != "general":
                continue

        results.append({
            "chunk_id": item.get("chunk_id"),
            "source_id": item.get("source_id"),
            "source": item.get("source"),
            "organization": item.get("organization"),
            "title": item.get("title"),
            "document_type": item.get("document_type"),
            "url": item.get("url"),
            "crop": item.get("crop"),
            "topic": item.get("topic"),
            "text": item.get("text"),
            "distance": float(distance),
        })

        if len(results) >= top_k:
            break

    results = rerank_results(results, crop=crop)

    return results[:top_k]
