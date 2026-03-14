from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("resource_id", "action_id", "scope", name="uq_permission_ras"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), index=True) # speeds up WHERE resouce_id = {id}
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id"), index=True)
    scope: Mapped[str] = mapped_column(String(100), default="own")

    resource = relationship("Resource")
    action = relationship("Action")
