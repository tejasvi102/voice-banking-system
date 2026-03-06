import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.migrations.session import Base

class UPIHandle(Base):
    __tablename__ = "upi_handles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=True)

    upi_id = Column(String(50), unique=True, nullable=False)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())