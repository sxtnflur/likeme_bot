from api.depends import PaymentUseCase
from fastapi import APIRouter, Request
from ..schemas.yookassa import WebhookPayload

router = APIRouter(prefix='/payment')


@router.post('/yookassa')
async def pay_yookassa(
    request: Request,
    payments_use_case: PaymentUseCase
) -> dict:
    body = await request.body()
    payload: WebhookPayload = WebhookPayload.parse_raw(body)
    await payments_use_case.on_payment(
        amount=payload.object.amount.value,
        metadata=payload.object.metadata
    )
    return {
        'status': 'OK'
    }