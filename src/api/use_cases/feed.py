from api.schemas.feed import FeedPost, Feed
from database import GeneratedImagesRepo, GeneratedImage
from database.repositories.generated_images import FeedOrdering
from database.repositories.likes import LikesRepo
from enums.categories import CategoriesEnum
from fastapi import HTTPException
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from services.remixing import RemixingService


class FeedUseCase:
    def __init__(self, db: AsyncSession,
                 remixing_service: RemixingService) -> None:
        self.db = db
        self.remixing_service = remixing_service

    def prepare_post(self, post: Row) -> FeedPost:
        post = post._mapping
        image = post.GeneratedImage
        return FeedPost.model_validate(
            image.__dict__ | {
                **post, 'remix_it_url': self.remixing_service.create_start_link(image.id),
            }
        )

    async def get_feed(
        self,
        user_id: int,
        ordering: FeedOrdering = FeedOrdering.all,
        categories: list[CategoriesEnum] | None = None,
        offset: int = 0, limit: int = 50
    ) -> Feed:
        posts = await GeneratedImagesRepo(self.db).get_feed(
            user_id=user_id,
            filters=dict(is_private=False),
            ordering=ordering,
            categories=categories,
            offset=offset,
            limit=limit
        )
        return Feed(
            posts=list(map(self.prepare_post, posts)),
            has_more=len(posts) == limit
        )

    async def get_post(self, user_id: int, post_id: int) -> FeedPost | None:
        post = await GeneratedImagesRepo(self.db).get_one_with_data(
            user_id=user_id,
            id=post_id
        )
        if post:
            return self.prepare_post(post)
        else:
            raise HTTPException(status_code=404)

    async def like_post(self, post_id: int, user_id: int) -> bool:
        """
        :param post_id:
        :param user_id:
        :return: True - пост лайкнут, False - лайк убран
        """
        if await LikesRepo(self.db).exists(image_id=post_id, user_id=user_id):
            await LikesRepo(self.db).delete(image_id=post_id, user_id=user_id)
            return False
        else:
            await LikesRepo(self.db).add(image_id=post_id, user_id=user_id)
            return True