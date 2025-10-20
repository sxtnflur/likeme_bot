from api.depends import FeedUseCase
from api.schemas.feed import FeedPost
from api.types import Offset, Limit
from database.repositories.generated_images import FeedStrategy
from fastapi import APIRouter, Body, Query
from typing_extensions import Annotated

router = APIRouter(prefix='/feed')


@router.get('')
async def get_feed(
    feed_use_case: FeedUseCase,
    strategy: Annotated[FeedStrategy, Query(...)] = FeedStrategy.NEWEST,
    offset: Offset = None,
    limit: Limit = 50
) -> list[FeedPost]:
    return await feed_use_case.get_feed(
        stategy=strategy, offset=offset, limit=limit
    )