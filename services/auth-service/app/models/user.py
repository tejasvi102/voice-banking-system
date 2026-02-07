<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.migrations.session import Base
from sqlalchemy.dialects.postgresql import UUID
<<<<<<< HEAD
=======
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.migrations.session import Base
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)

class User(Base):
    __tablename__ = "users"

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
    id = Column(
                UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                index=True
            )
<<<<<<< HEAD
=======
    id = Column(Integer, primary_key=True, index=True)
>>>>>>> cae5671 (Implement authentication service with user registration and login endpoints)
=======
>>>>>>> c25f695 (Enhance authentication service: add RegisterResponse schema, update user model to use UUID, and modify registration endpoint response. Create tables script for database initialization.)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
