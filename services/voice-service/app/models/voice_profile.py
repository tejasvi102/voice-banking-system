import uuid
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.migrations.session import Base

class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)

    # ECAPA embedding size = 192
    embedding = Column(Vector(192), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
