from pydantic import BaseModel


class PaymentAmount(BaseModel):
    value: float
    currency: str


class WebhookObject(BaseModel):
    id: str
    status: str
    metadata: dict = {}
    payment_method: dict | None = None
    amount: PaymentAmount


class WebhookPayload(BaseModel):
    event: str
    object: WebhookObject