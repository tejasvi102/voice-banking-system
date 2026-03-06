from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID
from typing import Optional

class ConfirmUPIRequest(BaseModel):
    upi_id: str
    card_id: Optional[UUID] = None
    is_primary: bool = False