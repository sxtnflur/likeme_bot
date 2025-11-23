from api.depends import PaymentUseCase
from fastapi import APIRouter, Request
from ..schemas.yookassa import WebhookPayload
from yookassa.domain.notification import WebhookNotification

router = APIRouter(prefix='/payment')


@router.post('/yookassa')
async def pay_yookassa(
    request: Request,
    payments_use_case: PaymentUseCase
) -> dict:
    print(f"{request.client.host=} {request.client.port=}")
    payload = WebhookNotification(**await request.json())

    await payments_use_case.on_payment(
        amount=payload.object.amount.value,
        metadata=payload.object.metadata
    )
    return {
        'status': 'OK'
    }