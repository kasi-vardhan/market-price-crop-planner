import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load backend/.env regardless of the terminal's working directory.
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to backend/.env."
        )

    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    return ChatGroq(
        model=model,
        temperature=0,
        max_retries=2,
        api_key=api_key,
    )
