from app.services.market_repository import (
    get_market_price_from_repository
)


def get_market_price(crop: str):

    return get_market_price_from_repository(
        crop
    )