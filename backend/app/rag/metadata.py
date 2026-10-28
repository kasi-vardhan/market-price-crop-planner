import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
METADATA_FILE = BASE_DIR / "knowledge_base" / "metadata" / "sources.json"


def load_source_metadata():

    if not METADATA_FILE.exists():
        return {}

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        sources = json.load(file)

    return {
        item["source_id"]: item
        for item in sources
    }


def detect_crop(source):

    source = source.lower()

    if "tomato" in source:
        return "tomato"
    if "chilli" in source:
        return "chilli"
    if "groundnut" in source:
        return "groundnut"
    if "paddy" in source or "rice" in source:
        return "paddy"
    if "green_gram" in source or "moong" in source:
        return "green_gram"
    if "bengal_gram" in source or "chickpea" in source or "chana" in source:
        return "bengal_gram"
    if "maize" in source or "corn" in source:
        return "maize"
    if "red_gram" in source or "tur" in source or "pigeonpea" in source or "arhar" in source:
        return "red_gram"
    if "cotton" in source:
        return "cotton"

    return "general"


def detect_topic(text):

    text = text.lower()

    topic_keywords = {

        "soil": [
            "soil",
            "sandy",
            "loamy",
            "clay",
            "drainage"
        ],

        "water": [
            "irrigation",
            "water",
            "rainfall",
            "moisture"
        ],

        "season": [
            "season",
            "kharif",
            "rabi",
            "sowing",
            "planting"
        ],

        "pest": [
            "pest",
            "insect",
            "thrips",
            "aphid",
            "borer"
        ],

        "disease": [
            "disease",
            "blight",
            "virus",
            "rot",
            "mildew"
        ],

        "cultivation": [
            "cultivation",
            "spacing",
            "seed",
            "transplanting",
            "fertilizer"
        ],

        "market": [
            "market",
            "price",
            "forecast",
            "mandi"
        ]
    }

    for topic, keywords in topic_keywords.items():

        for keyword in keywords:

            if keyword in text:
                return topic

    return "general"


def detect_source_id(source):

    source = source.lower()

    if "tomato" in source:
        return "icar_tomato"

    if "chilli" in source:
        return "icar_chilli"

    if "groundnut" in source:
        return "icar_groundnut"

    if "paddy" in source:
        return "icar_paddy"

    if "green_gram" in source:
        return "icar_green_gram"

    if "bengal_gram" in source:
        return "icar_bengal_gram"

    if "maize" in source:
        return "icar_maize"

    if "red_gram" in source:
        return "icar_red_gram"

    if "cotton" in source:
        return "icar_cotton"

    if "andhra_pradesh" in source:
        return "tnau_crop_knowledge"

    return "icar_kharif_2025"
