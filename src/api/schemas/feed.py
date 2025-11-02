from pydantic import BaseModel, computed_field


class FeedUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    avatar_url: str | None = None

    class Config:
        from_attributes = True

    @computed_field
    @property
    def name(self) -> str:
        if self.last_name is not None:
            return self.first_name + ' ' + self.last_name
        return self.first_name


class FeedPost(BaseModel):
    id: int
    image_url: str
    prompt: str
    user: FeedUser
    is_liked: bool
    remix_it_url: str
    count_likes: int

    class Config:
        from_attributes = True
