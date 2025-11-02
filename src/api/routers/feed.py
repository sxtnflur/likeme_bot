from api.depends import FeedUseCase, AuthedUser
from api.schemas.feed import FeedPost, Feed
from api.types import Offset, Limit
from database.repositories.generated_images import FeedOrdering
from fastapi import APIRouter, Body, Query
from typing_extensions import Annotated
from enums.categories import CategoriesEnum

router = APIRouter(prefix='/feed')


@router.get('')
async def get_feed(
    user: AuthedUser,
    feed_use_case: FeedUseCase,
    ordering: Annotated[FeedOrdering, Query(...)] = FeedOrdering.all,
    category: Annotated[CategoriesEnum | None, Query(...)] = None,
    offset: Offset = None,
    limit: Limit = 50
) -> Feed:
    return await feed_use_case.get_feed(
        user_id=user.id,
        ordering=ordering,
        categories=[category] if category else None,
        offset=offset, limit=limit
    )


@router.get('/{post_id}')
async def get_post(
    user: AuthedUser,
    feed_use_case: FeedUseCase,
    post_id: int
) -> FeedPost:
    return await feed_use_case.get_post(
        user_id=user.id,
        post_id=post_id
    )


@router.post('/like/{post_id}')
async def like_post(
    user: AuthedUser,
    post_id: int,
    feed_use_case: FeedUseCase
) -> dict:
    is_liked = await feed_use_case.like_post(post_id=post_id, user_id=user.id)
    return {
        'is_liked': is_liked
    }