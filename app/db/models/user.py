from sqlalchemy.orm import mapped_column, Mapped # maps sql table to python (ORM)
from sqlalchemy import String, Boolean # typehints

from app.db.base import BaseModel

class User(BaseModel):
    __tablename__ = "users" #will be used in queries

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True) # indexing speeds up queries and filtering
    hashed_password: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)

    