from pydantic import BaseModel, ConfigDict, Field


class ActionBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=255)


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=255)


class ActionRead(ActionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ActionDelete(BaseModel):
    id: int
