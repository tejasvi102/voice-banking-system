import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.migrations.session import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    card_type = Column(String(20), nullable=False)
    card_network = Column(String(20), nullable=False)
    last4 = Column(String(4), nullable=False)

    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())