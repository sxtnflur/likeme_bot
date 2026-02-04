from typing import cast

from aiogram.utils.deep_linking import create_deep_link
from config import settings


def create_remix_link(generated_image_id: int):
    payload = f'remix-{generated_image_id}'
    return create_deep_link(
        username=cast(str, settings.BOT_USERNAME),
        link_type="start",
        payload=payload,
        encode=True,
        encoder=None
    )