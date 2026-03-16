from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead
from app.schemas.role import RoleRead



class UserRoleBase(BaseModel):
    user_id: int
    role_id: int


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    user_id: int | None = None
    role_id: int | None = None


class UserRoleRead(UserRoleBase):
    user: UserRead
    role: RoleRead
    model_config = ConfigDict(from_attributes=True)


class UserRoleDelete(UserRoleBase):
    pass
