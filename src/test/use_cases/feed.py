import asyncio
import unittest
from api.depends import get_feed_use_case
from database.engine import async_session
from database.repositories.generated_images import FeedOrdering
from enums.categories import CategoriesEnum
from services.categories import CategoriesService


class TestFeedUseCase(unittest.TestCase):
    def test_get_feed(self):
        async def do():
            async with async_session() as session:
                use_case = get_feed_use_case(session)

                feed = await use_case.get_feed(
                    ordering=FeedOrdering.top,
                    categories=None,
                    offset=0,
                    limit=50
                )
                print(f'{feed=}')
                return
                categories = CategoriesService.category_keys
                orderings = [FeedOrdering.all, FeedOrdering.new, FeedOrdering.top]
                for category in (categories + [None]):
                    print(f'{category=}')
                    for ordering in orderings:
                        print(f'{ordering=}')
                        feed = await use_case.get_feed(
                            ordering=ordering,
                            categories=[category] if category else category,
                            offset=0,
                            limit=50
                        )
                        print(f'{feed=}')
                        if category == 'fantasy' or category is None:
                            assert feed != []
                        else:
                            assert feed == []

        asyncio.get_event_loop().run_until_complete(do())