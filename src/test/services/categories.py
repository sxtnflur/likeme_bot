import asyncio
import unittest

from depends import openai_service
from services.categories import CategoriesService


class TestCategories(unittest.TestCase):
    def test_gen_categories(self):
        async def do():
            url = 'https://bigling.ru/cdn/likeme/generated_images/1304563494/1760968043_0x1.a3d8f5aa1d97fp+30.jpg'
            categories_service = CategoriesService(openai=openai_service)
            res = await categories_service.generate_categories_for_image(
                image_url=url
            )
            print(f'{res=}')
        asyncio.get_event_loop().run_until_complete(do())