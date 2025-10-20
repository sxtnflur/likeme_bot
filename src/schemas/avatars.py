from pydantic import BaseModel


class AvatarSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True