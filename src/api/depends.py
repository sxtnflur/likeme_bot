from api.use_cases.payment import PaymentUseCase as PaymentUseCaseImpl
from api.use_cases.feed import FeedUseCase as FeedUseCaseImpl
from api.use_cases.fal_webhook import FalWebhookUseCase as FalWebhookUseCaseImpl
from database.engine import get_db
from depends import payments_service
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated
from depends import avatars_service


Db = Annotated[AsyncSession, Depends(get_db)]




def get_payments_use_case(
    db: Db
):
    return PaymentUseCaseImpl(db, payments_service=payments_service)


PaymentUseCase = Annotated[PaymentUseCaseImpl, Depends(get_payments_use_case)]


def get_feed_use_case(
    db: Db
):
    return FeedUseCaseImpl(db)


FeedUseCase = Annotated[FeedUseCaseImpl, Depends(get_feed_use_case)]


def get_fal_webhook_use_case(
    db: Db
) -> FalWebhookUseCaseImpl:
    return FalWebhookUseCaseImpl(db=db, avatars_service=avatars_service)


FalWebhookUseCase = Annotated[FalWebhookUseCaseImpl, Depends(get_fal_webhook_use_case)]