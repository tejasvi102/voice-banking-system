from pydantic import BaseModel
from typing import Literal

class CardCreateRequest(BaseModel):
    card_type: Literal["debit", "credit"]
    card_network: Literal["VISA", "MASTERCARD", "RUPAY"]
    last4: str
    expiry_month: int
    expiry_year: int