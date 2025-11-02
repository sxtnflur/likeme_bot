from pydantic import BaseModel


class FeedUser(BaseModel):
    id: int
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class FeedPost(BaseModel):
    id: int
    image_url: str
    prompt: str
    user: FeedUser
    remix_it_url: str

    class Config:
        from_attributes = True
