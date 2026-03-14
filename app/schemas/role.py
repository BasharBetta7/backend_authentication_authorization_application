from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=255)


class RoleCreate(RoleBase):
    pass



class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=255)


class RoleRead(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class RoleDelete(BaseModel):
    id: int
