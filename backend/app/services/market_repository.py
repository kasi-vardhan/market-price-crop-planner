from app.models.market import MarketPrice


MARKET_DATA = {
    "tomato": MarketPrice(
        crop="tomato",
        market="Ongole",
        location="Andhra Pradesh",
        date="2026-10-07",
        min_price=20,
        max_price=30,
        modal_price=25,
        source="demo"
    ),
    "chilli": MarketPrice(
        crop="chilli",
        market="Guntur",
        location="Andhra Pradesh",
        date="2026-10-07",
        min_price=100,
        max_price=140,
        modal_price=120,
        source="demo"
    ),
    "groundnut": MarketPrice(
        crop="groundnut",
        market="Markapur",
        location="Andhra Pradesh",
        date="2026-10-07",
        min_price=60,
        max_price=80,
        modal_price=70,
        source="demo"
    ),
    "paddy": MarketPrice(
        crop="paddy",
        market="Ongole",
        location="Andhra Pradesh",
        date="2026-10-07",
        min_price=22,
        max_price=28,
        modal_price=25,
        source="demo"
    )
}


def get_market_price_from_repository(crop: str):
    crop = crop.lower().strip()

    market = MARKET_DATA.get(crop)

    if not market:
        return {
            "error": f"No market data available for {crop}"
        }

    return market.model_dump()
