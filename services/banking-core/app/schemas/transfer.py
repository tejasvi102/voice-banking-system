from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID


class TransferRequest(BaseModel):
    from_user_id: UUID
    to_upi_id: str
    amount: Decimal
    currency: str = "INR"
    idempotency_key: str

class UPITransferRequest(BaseModel):
    from_user_id: str
    to_upi_id: str
    amount: Decimal
    currency: str
    idempotency_key: str