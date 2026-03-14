from pydantic import BaseModel, ConfigDict


class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):
    role_id: int | None = None
    permission_id: int | None = None


class RolePermissionRead(RolePermissionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RolePermissionDelete(BaseModel):
    id: int
