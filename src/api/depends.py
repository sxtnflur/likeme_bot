from api.use_cases.payment import PaymentUseCase as PaymentUseCaseImpl
from api.use_cases.feed import FeedUseCase as FeedUseCaseImpl
from database.engine import get_db
from depends import payments_service
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

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