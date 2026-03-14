from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.db.base import BaseModel

class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id : Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    permission_id : Mapped[int] = mapped_column(ForeignKey("permissions.id"), index= True)

    role = relationship("Role")
    permission = relationship("Permission")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="unq_role_permission"), 
    )