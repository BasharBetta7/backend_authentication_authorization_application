from sqlalchemy import String, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

