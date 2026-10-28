from pydantic import BaseModel
from typing import Optional


class MarketPrice(BaseModel):
    crop: str
    market: str
    location: Optional[str] = None
    date: Optional[str] = None

    min_price: float
    max_price: float
    modal_price: float

    source: str = "demo"
