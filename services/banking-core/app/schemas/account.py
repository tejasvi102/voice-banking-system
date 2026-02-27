from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class AccountCreateRequest(BaseModel):
    user_id: UUID
    currency: str = "INR"
    initial_balance: Decimal = 0


class AccountResponse(BaseModel):
    user_id: UUID
    balance: Decimal
    currency: str
    status: str