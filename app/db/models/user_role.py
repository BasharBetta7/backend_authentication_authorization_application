from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True) # two primary keys mean that the pair(user.id, roles.id) should be unique in user_role

    user = relationship("User") # stores the corresponding user python object as attribute (sql resolve it from user_id)
    role = relationship("Role")


