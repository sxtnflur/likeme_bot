import asyncio
import unittest
from depends import avatars_service


class TestAvatarsService(unittest.TestCase):
    def test_prepare_images(self):
        async def do():
            zip_url = await avatars_service.prepare_images(file_ids=[
                'AgACAgIAAxkBAAIaRmkWDlLjb_X8BNmwgU7PaiXQJIioAAJzEGsbZQewSKjjSImAINwBAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaSGkWDlICiZl5ygYGlBt2WveZ45RBAAJ1EGsbZQewSPM_rODGnzVNAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaSWkWDlLT9CVtYdrvvpsPXtqF5unIAAJ2EGsbZQewSBrz3bFWIhzNAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaR2kWDlJ18TB1tQKH0VQsYTf7xZT2AAJ0EGsbZQewSDoqyL2SChHuAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaS2kWDlIwGWMVjPymf8T4C36xma3TAAJ4EGsbZQewSIMQxzMtMWCYAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaTmkWDlIHxPxb_TRLKJzGGBMNQTEqAAJ7EGsbZQewSPQElLMX1B3FAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaT2kWDlJdI8yjhaMpagoRV7Z4R0uJAAJ8EGsbZQewSOxgs-TmeMWYAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaTGkWDlJ4kH7gh60ajBpQYERi7xK2AAJ5EGsbZQewSAMhi7-t7PlbAQADAgADeAADNgQ',
                'AgACAgIAAxkBAAIaSmkWDlJsBvNgq3IurjXhvCJR8wuSAAJ3EGsbZQewSAKac_rd0N_SAQADAgADeQADNgQ',
                'AgACAgIAAxkBAAIaTWkWDlLrIUDxRFj-ljPREZ8NdQ4UAAJ6EGsbZQewSARjMhp-YLOjAQADAgADeQADNgQ'
            ])
            print(f'{zip_url=}')
        asyncio.get_event_loop().run_until_complete(do())
