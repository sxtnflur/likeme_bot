import fal_client
import os

from aiogram import Bot
from config import settings
from typing_extensions import Literal
import zipfile
import io

# QUEUE_URL = "fal-ai/flux-lora-portrait-trainer"
QUEUE_URL = "fal-ai/flux-krea-trainer"


async def train_lora(dataset_url: str, metadata: dict | None = None) -> str:
    args = {
        "images_data_url": dataset_url,
        "steps": 1000,
        "learning_rate": 0.0002,
        "trigger_word": settings.TRIGGER_WORD
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
        'enable_safety_checker': False,
        "enable_prompt_expansion": False
    }

    if lora:
        # PIXEL: {'path': 'https://huggingface.co/Shakker-Labs/FLUX.1-Kontext-dev-LoRA-Pixel-Style/resolve/main/FLUX
        # -kontext-lora-pixel-style.safetensors', 'scale': 1.5}

        # { "path": "https://huggingface.co/Shakker-Labs/FLUX.1-Kontext-dev-LoRA-Felt-Style"
        # "/rezolve/main/FLUX-kontext-lora-felt-style.safetensors", "scale": 1 }
        arguments["loras"] = [{"path": lora, "scale": 1}]

    model = 'fal-ai/flux-lora'
    handler = await fal_client.submit_async(model, arguments=arguments)
    result = await handler.get()
    return list(map(lambda image: image['url'], result["images"]))


async def image2image(
    prompt: str,
    image_url: str,
    lora: str,
    photo_format: tuple[int, int],
    strength: float = 0.85,
    num_images: Literal[1, 2] = 1,
):
    arguments = {
        "prompt": prompt,
        "image_url": image_url,
        "image_size": {
            "width": photo_format[0],
            "height": photo_format[1]
        },
        "strength": strength,
        "num_images": num_images,
        'enable_safety_checker': False
    }

    if lora:
        arguments["loras"] = [{"path": lora, "scale": 1}]

    model = 'fal-ai/flux-lora/image-to-image'
    handler = await fal_client.submit_async(model, arguments=arguments)
    result = await handler.get()
    return list(map(lambda image: image['url'], result["images"]))



async def gen_image_general(prompt: str, lora: str):
    data = {
        "prompt": prompt,
        "image_size": "square_hd",
        "num_inference_steps": 25,
        "guidance_scale": 3.5,
        "loras": [
            {
                "path": lora,
                "scale": 1.0
            }
        ],
        "ip_adapters": [
            {
                "path": "TencentARC/IP-Adapter-FaceID",
                "image_url": "https://s3.twcstorage.ru/3899d0fe-16d22abf-cc69-419f-8e92-e820192d491c/avatars/simple/1763995653_8492062148.jpg",
                "scale": 0.8
            }
        ]
    }