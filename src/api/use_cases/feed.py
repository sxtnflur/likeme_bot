from api.schemas.feed import FeedPost
from database import GeneratedImagesRepo
from database.repositories.generated_images import FeedOrdering
from enums.categories import CategoriesEnum
from sqlalchemy.ext.asyncio import AsyncSession


class FeedUseCase:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_feed(
        self, ordering: FeedOrdering = FeedOrdering.all,
        categories: list[CategoriesEnum] | None = None,
        offset: int = 0, limit: int = 50
    ) -> list[FeedPost]:
        posts = await GeneratedImagesRepo(self.db).get_feed(
            filters=dict(is_private=False),
            ordering=ordering,
            categories=categories,
            offset=offset,
            limit=limit
        )
        return list(map(FeedPost.model_validate, posts))