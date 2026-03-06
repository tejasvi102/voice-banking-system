from sqlalchemy import Column, ForeignKey, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.migrations.session import Base


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))

    entry_type = Column(String, nullable=False)  # debit / credit

    amount = Column(Numeric(18, 2), nullable=False)

    currency = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
