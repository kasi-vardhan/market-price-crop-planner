import pickle
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from app.rag.rag_service import (
    load_documents,
    prepare_chunks
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
INDEX_PATH = BASE_DIR / "knowledge_base" / "processed" / "index.faiss"
METADATA_PATH = BASE_DIR / "knowledge_base" / "processed" / "metadata.pkl"


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


documents = load_documents()

print(
    f"Documents loaded: {len(documents)}"
)

chunks = prepare_chunks(
    documents
)

print(
    f"Chunks created: {len(chunks)}"
)


texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = model.encode(
    texts,
    convert_to_numpy=True
)


dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(embeddings)


INDEX_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


faiss.write_index(
    index,
    str(INDEX_PATH)
)


with open(
    METADATA_PATH,
    "wb"
) as file:

    pickle.dump(
        chunks,
        file
    )


print(
    f"Created index with {len(chunks)} chunks from {len(documents)} documents successfully."
)
