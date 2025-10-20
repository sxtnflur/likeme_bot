import fal_client
from config import settings
from typing_extensions import Literal

QUEUE_URL = "fal-ai/flux-lora-portrait-trainer"


async def upload_zip(images_data_url):
    url = fal_client.upload_file(images_data_url)
    return url


async def train_lora(dataset_url, tg_id):
    handler = await fal_client.submit_async(
        QUEUE_URL,
        arguments={
            "images_data_url": dataset_url,
            "steps": 1000,
            "learning_rate": 0.0002,
        },
        webhook_url=settings.TRAIN_CALLBACK_URL
    )
    request_id = handler.request_id


    # TRAINING_JOBS[request_id] = (tg_id, 'lora')
    return request_id





async def generate_image(prompt, lora, photo_format):
    print(lora)

    arguments = {
        "prompt": prompt,
        "image_size": {
            "width": photo_format[0],
            "height": photo_format[1]
        }
    }

    if lora:
        arguments["loras"] = [{"path": lora, "scale": 1}]

    handler = await fal_client.submit_async("fal-ai/flux-lora", arguments=arguments)

    async for event in handler.iter_events():
        print(event)

    result = await handler.get()
    return result


async def generate_images(prompt, lora, photo_format, num_images: Literal[1, 2] = 1):

    arguments = {
        "prompt": prompt,
        "image_size": {
            "width": photo_format[0],
            "height": photo_format[1]
        },
        "num_images": num_images,
        'enable_safety_checker': False
    }

    if lora:
        arguments["loras"] = [{"path": lora, "scale": 1}]

    handler = await fal_client.submit_async("fal-ai/flux-lora", arguments=arguments)

    async for event in handler.iter_events():
        print(event)

    result = await handler.get()
    return result

