import abc
import dataclasses
from datetime import datetime

import aiohttp
from typing_extensions import Literal

PaymentType = Literal['first-offer', 'second-offer', 'package',
                      'generations-image', 'generations-video', 'generations-text',
                      'avatar', 'custom']

payments_descriptions: dict[Literal["first-offer", "generations", "avatar"], str] = {
    'first-offer': 'Первый платеж за {price:,}₽ для аккаунта с tg id = {user_id}.',
    'generations': '{requests} генераций {callback_data.type} за {price:,}₽ для '
                   'аккаунта с tg id = {user_id}',
    'avatar': '+ 1 аватар за {price}₽ для аккаунта с tg id = {user_id}'
}


def get_payment_description(type: Literal["first-offer", "generations", "avatar"],
                            price: int, user_id: int, generations: int | None = None) -> str:
    match type:
        case 'generations':
            if not generations:
                return f'Генерации {type} за {price:,}₽ для аккаунта с tg id = {user_id}'
            return f'{generations} генераций {type} за {price:,}₽ для ' \
                   f'аккаунта с tg id = {user_id}'
        case 'first-offer':
            return f'Первый платеж за {price:,}₽ для аккаунта с tg id = {user_id}.'
        case 'avatar':
            return f'+ 1 аватар за {price}₽ для аккаунта с tg id = {user_id}'
        case _:
            return f'Оплата {type} за {price:,}₽ для аккаунта с tg id = {user_id}'

@dataclasses.dataclass
class PaymentData:
    id: str
    url: str


class AbstractPaymentService(abc.ABC):
    @abc.abstractmethod
    async def create_payment(self, amount: int, description: str, test: bool = False,
                             metadata: dict | None = None,
                             expired_date: datetime | None = None,
                             session: aiohttp.ClientSession | None = None) -> PaymentData:
        ...
