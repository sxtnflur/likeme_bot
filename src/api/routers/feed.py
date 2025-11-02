from api.depends import FeedUseCase
from api.schemas.feed import FeedPost
from api.types import Offset, Limit
from database.repositories.generated_images import FeedOrdering
from fastapi import APIRouter, Body, Query
from typing_extensions import Annotated
from enums.categories import CategoriesEnum

router = APIRouter(prefix='/feed')


@router.get('')
async def get_feed(
    feed_use_case: FeedUseCase,
    ordering: Annotated[FeedOrdering, Query(...)] = FeedOrdering.all,
    category: Annotated[CategoriesEnum | None, Query(...)] = None,
    offset: Offset = None,
    limit: Limit = 50
) -> list[FeedPost]:
    return await feed_use_case.get_feed(
        ordering=ordering,
        categories=[category] if category else None,
        offset=offset, limit=limit
    )


@router.get('/{post_id}')
async def get_post(
    feed_use_case: FeedUseCase,
    post_id: int
) -> FeedPost:
    return await feed_use_case.get_post(post_id)