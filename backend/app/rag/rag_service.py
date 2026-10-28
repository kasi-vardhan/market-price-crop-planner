from pathlib import Path

from app.rag.metadata import (
    load_source_metadata,
    detect_crop,
    detect_topic,
    detect_source_id
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DOCUMENTS_PATH = BASE_DIR / "knowledge_base" / "documents"


def load_documents():

    documents = []

    source_metadata = (
        load_source_metadata()
    )

    for file_path in DOCUMENTS_PATH.rglob("*"):

        if file_path.suffix.lower() not in {
            ".txt",
            ".md"
        }:
            continue

        if not file_path.is_file():
            continue

        try:

            text = file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            continue

        relative_source = str(
            file_path.relative_to(
                DOCUMENTS_PATH
            )
        ).replace("\\", "/")

        crop = detect_crop(
            relative_source
        )

        source_id = detect_source_id(
            relative_source
        )

        source_info = (
            source_metadata.get(
                source_id,
                {}
            )
        )

        documents.append(
            {
                "source": relative_source,

                "source_id": source_id,

                "organization": source_info.get(
                    "organization",
                    "Unknown"
                ),

                "title": source_info.get(
                    "title",
                    file_path.stem
                ),

                "document_type": source_info.get(
                    "document_type",
                    "unknown"
                ),

                "url": source_info.get(
                    "url"
                ),

                "crop": crop,

                "text": text
            }
        )

    return documents


def chunk_text(
    text,
    chunk_size=120,
    overlap=30
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(
            chunk
        )

        if end == len(words):
            break

        start = end - overlap

    return chunks


def prepare_chunks(documents):

    chunks = []

    for document in documents:

        text_chunks = chunk_text(
            document["text"]
        )

        for index, chunk in enumerate(
            text_chunks
        ):

            topic = detect_topic(
                chunk
            )

            chunk_id = (
                f"{document['source_id']}_"
                f"{document['crop']}_"
                f"{index + 1:04d}"
            )

            chunks.append(
                {
                    "chunk_id": chunk_id,

                    "source_id": document[
                        "source_id"
                    ],

                    "source": document[
                        "source"
                    ],

                    "organization": document[
                        "organization"
                    ],

                    "title": document[
                        "title"
                    ],

                    "document_type": document[
                        "document_type"
                    ],

                    "url": document[
                        "url"
                    ],

                    "crop": document[
                        "crop"
                    ],

                    "topic": topic,

                    "text": chunk
                }
            )

    return chunks


def get_relevant_knowledge(query, top_k=3, crop=None):
    from app.rag.retriever import search_knowledge
    return search_knowledge(
        query=query,
        crop=crop,
        top_k=top_k
    )
