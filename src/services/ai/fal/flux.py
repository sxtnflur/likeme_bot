import fal_client
import os

from aiogram import Bot
from config import settings
from typing_extensions import Literal
import zipfile
import io

QUEUE_URL = "fal-ai/flux-lora-portrait-trainer"


async def train_lora(dataset_url: str, metadata: dict | None = None) -> str:
    args = {
        "images_data_url": dataset_url,
        "steps": 1000,
        "learning_rate": 0.0002
    }
    if metadata:
        args.update(metadata=metadata)
    handler = await fal_client.submit_async(
        QUEUE_URL,
        arguments=args,
        webhook_url=settings.TRAIN_CALLBACK_URL
    )
    request_id = handler.request_id
    return request_id


async def generate_images(
        prompt: str, lora: str, photo_format: tuple[int, int],
        num_images: Literal[1, 2] = 1
) -> list[str]:

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
        # PIXEL: {'path': 'https://huggingface.co/Shakker-Labs/FLUX.1-Kontext-dev-LoRA-Pixel-Style/resolve/main/FLUX
        # -kontext-lora-pixel-style.safetensors', 'scale': 1.5}

        # { "path": "https://huggingface.co/Shakker-Labs/FLUX.1-Kontext-dev-LoRA-Felt-Style"
        # "/rezolve/main/FLUX-kontext-lora-felt-style.safetensors", "scale": 1 }
        arguments["loras"] = [{"path": lora, "scale": 1}]

    model = 'fal-ai/flux-lora'
    handler = await fal_client.submit_async(model, arguments=arguments)

    async for event in handler.iter_events():
        print(event)

    result = await handler.get()
    return list(map(lambda image: image['url'], result["images"]))

