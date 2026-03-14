from pydantic import BaseModel, ConfigDict


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    user_id: int | None = None
    role_id: int | None = None


class UserRoleRead(UserRoleBase):
    model_config = ConfigDict(from_attributes=True)


class UserRoleDelete(UserRoleBase):
    pass
