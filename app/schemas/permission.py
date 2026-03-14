from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    resource_id: int
    action_id: int
    scope: str = Field(default="own", min_length=1, max_length=100)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    resource_id: int | None = None
    action_id: int | None = None
    scope: str | None = Field(default=None, min_length=1, max_length=100)


class PermissionRead(PermissionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PermissionDelete(BaseModel):
    id: int
