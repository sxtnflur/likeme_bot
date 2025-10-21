import asyncio
import unittest
from api.depends import get_feed_use_case
from database.engine import async_session
from database.repositories.generated_images import FeedOrdering


class TestFeedUseCase(unittest.TestCase):
    def test_get_feed(self):
        async def do():
            async with async_session() as session:
                use_case = get_feed_use_case(session)
                orderings = [FeedOrdering.all, FeedOrdering.new, FeedOrdering.top]
                for ordering in orderings:
                    feed = await use_case.get_feed(
                        ordering=ordering,
                        offset=0,
                        limit=50
                    )
                    print(f'{feed=}')

        asyncio.get_event_loop().run_until_complete(do())