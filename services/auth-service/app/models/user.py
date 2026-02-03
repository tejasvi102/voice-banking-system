<<<<<<< HEAD
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.migrations.session import Base
from sqlalchemy.dialects.postgresql import UUID
=======
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.migrations.session import Base
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)

class User(Base):
    __tablename__ = "users"

<<<<<<< HEAD
    id = Column(
                UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                index=True
            )
=======
    id = Column(Integer, primary_key=True, index=True)
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
