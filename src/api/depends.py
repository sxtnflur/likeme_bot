from aiogram.utils.web_app import WebAppUser
from api.use_cases.auth import AuthUseCase as AuthUseCaseImpl
from api.use_cases.payment import PaymentUseCase as PaymentUseCaseImpl
from api.use_cases.feed import FeedUseCase as FeedUseCaseImpl
from api.use_cases.fal_webhook import FalWebhookUseCase as FalWebhookUseCaseImpl
from database.engine import get_db
from depends import payments_service
from fastapi import Depends, Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.remixing import RemixingService as RemixingService_
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated
from depends import avatars_service, users_service
from bot.loader import bot


Db = Annotated[AsyncSession, Depends(get_db)]

def get_remixing_service():
    return RemixingService_(bot=bot)

RemixingService = Annotated[RemixingService_, Depends(get_remixing_service)]


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


def get_auth_use_case(
    db: Db
):
    return AuthUseCaseImpl(
        db=db, users_service=users_service
    )


AuthUseCase = Annotated[AuthUseCaseImpl, Depends(get_auth_use_case)]


async def get_current_user(
    auth: AuthUseCase,
    token: HTTPAuthorizationCredentials = Security(HTTPBearer())
) -> WebAppUser:
    user = await auth.auth_by_telegram_init_data(init_data=token.credentials)
    if not user:
        raise HTTPException(status_code=403, detail='Невалидная инит дата')
    return user


AuthedUser = Annotated[WebAppUser, Depends(get_current_user)]