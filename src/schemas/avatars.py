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


AvatarStatusType = Literal['added', 'in_progress', 'ready']


class AvatarSchema(BaseModel):
    id: int
    name: str | None = None
    level: int
    model_data: str | None = None
    status: AvatarStatusType

    class Config:
        from_attributes = True