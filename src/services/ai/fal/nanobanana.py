import fal_client
from PIL.Image import Image
from typing_extensions import Literal


async def edit_image(
        prompt: str,
        images: list[Image],
        num_images: int,
        aspect_ratio: Literal['21:9', '1:1', '4:3', '3:2', '2:3', '5:4', '4:5', '3:4', '16:9', '9:16'] | None = None
) -> list[str]:
    image_urls = [await fal_client.upload_image_async(image=image) for image in images]
    handler = await fal_client.submit_async(
        'fal-ai/nano-banana/edit',
        arguments={
            'prompt': prompt,
            'image_urls': image_urls,
            'num_images': num_images,
            'aspect_ratio': aspect_ratio
        }
    )
    data = await handler.get()
    return [image.get('url') for image in data.get('images')]