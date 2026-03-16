from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime
from app.db.base import BaseModel

class Event(BaseModel):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    description: Mapped[str] = mapped_column(String(255))


