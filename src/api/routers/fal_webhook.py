from api.depends import FalWebhookUseCase
from fastapi import APIRouter, Request

router = APIRouter(prefix='/fal_webhook', include_in_schema=False)


@router.post('/train-model')
async def train_model(
    request: Request,
    fal_use_case: FalWebhookUseCase
) -> dict:
    await fal_use_case.on_created_model(body=await request.body())
    return {"ok": True}