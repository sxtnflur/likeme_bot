from api.schemas.feed import FeedPost
from database import GeneratedImagesRepo, GeneratedImage
from database.repositories.generated_images import FeedOrdering
from enums.categories import CategoriesEnum
from sqlalchemy.ext.asyncio import AsyncSession
from services.remixing import RemixingService


class FeedUseCase:
    def __init__(self, db: AsyncSession,
                 remixing_service: RemixingService) -> None:
        self.db = db
        self.remixing_service = remixing_service

    async def get_feed(
        self, ordering: FeedOrdering = FeedOrdering.all,
        categories: list[CategoriesEnum] | None = None,
        offset: int = 0, limit: int = 50
    ) -> list[FeedPost]:
        def prepare_post(post: GeneratedImage) -> FeedPost:
            return FeedPost.model_validate(
                post.__dict__ | {'remix_it_url': self.remixing_service.create_start_link(post.id)}
            )

        posts = await GeneratedImagesRepo(self.db).get_feed(
            filters=dict(is_private=False),
            ordering=ordering,
            categories=categories,
            offset=offset,
            limit=limit
        )
        return list(map(prepare_post, posts))