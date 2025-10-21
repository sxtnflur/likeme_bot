from enums import ModelStatusType
from pydantic import BaseModel
from typing_extensions import Literal


class Model(BaseModel):
    id: int
    avatar_id: int
    level: int
    photos: list[str] | None = None
    diffusers_url: str | None = None
    status: ModelStatusType = 'ready'

    class Config:
        from_attributes = True


class AvatarSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class AvatarWithModelsSchema(AvatarSchema):
    models: list[Model]

    class Config:
        from_attributes = True