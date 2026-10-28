from app.crop_data import CROPS

CROP_ALIASES = {
    "tomato": ["tomato", "tamatar"],
    "chilli": ["chilli", "chili", "mirchi", "chilli red", "red chilli"],
    "groundnut": ["groundnut", "peanut", "mungfali", "ground nut"],
    "paddy": ["paddy", "rice", "dhan"],
    "green_gram": ["green gram", "green_gram", "greengram", "moong", "mung", "pesalu"],
    "bengal_gram": ["bengal gram", "bengal_gram", "bengalgram", "chana", "chickpea", "sanagalu"],
    "maize": ["maize", "corn", "makka", "makkajonna"],
    "red_gram": ["red gram", "red_gram", "redgram", "tur", "arhar", "pigeonpea", "pigeon pea", "kandulu"],
    "cotton": ["cotton", "kapas", "prathi"]
}


def detect_crop(text: str):
    if not text:
        return None

    cleaned = text.lower()
    matches = []

    for crop_key, aliases in CROP_ALIASES.items():
        for alias in aliases:
            if alias in cleaned:
                matches.append(crop_key)
                break

    for crop_key, crop_data in CROPS.items():
        crop_name = crop_data.get("name", crop_key).lower()
        if crop_key in cleaned or crop_name in cleaned:
            matches.append(crop_key)

    unique_matches = list(dict.fromkeys(matches))

    if len(unique_matches) == 1:
        return unique_matches[0]

    return None
