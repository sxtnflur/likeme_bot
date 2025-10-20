from api.schemas.feed import FeedPost
from database import GeneratedImagesRepo
from database.repositories.generated_images import FeedStrategy
from sqlalchemy.ext.asyncio import AsyncSession


class FeedUseCase:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_feed(
        self, stategy: FeedStrategy = FeedStrategy.NEWEST, offset: int = 0, limit: int = 50
    ) -> list[FeedPost]:
        posts = await GeneratedImagesRepo(self.db).get_list_with_user(
            filters=dict(),
            strategy=stategy,
            offset=offset,
            limit=limit
        )
        return list(map(FeedPost.model_validate, posts))