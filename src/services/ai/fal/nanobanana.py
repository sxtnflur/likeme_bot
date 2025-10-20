import fal_client
from PIL.Image import Image


async def edit_image(
        prompt: str,
        images: list[Image],
        num_images: int
) -> list[str]:
    image_urls = [await fal_client.upload_image_async(image=image) for image in images]
    handler = await fal_client.submit_async(
        'fal-ai/nano-banana/edit',
        arguments={
            'prompt': prompt,
            'image_urls': image_urls,
            'num_images': num_images
        }
    )
    data = await handler.get()
    return [image.get('url') for image in data.get('images')]