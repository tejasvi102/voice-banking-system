from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID


class TransferValidationRequest(BaseModel):
    from_user_id: UUID
    to_user_id: UUID
    amount: Decimal
    currency: str = "INR"