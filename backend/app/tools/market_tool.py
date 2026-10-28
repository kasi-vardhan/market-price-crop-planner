from app.services.reliable_market_service import (
    get_reliable_market_price
)


def market_price_tool(crop: str):

    return get_reliable_market_price(
        crop=crop
    )
