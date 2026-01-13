from aiogram.filters.callback_data import CallbackData


class PaymentStartCallback(CallbackData, prefix='payment'): ...

class BuyImageGenerationsCallback(CallbackData, prefix='buy-image-gens'): ...

class SelectImageGenerationsCallback(CallbackData, prefix='select-image-package'):
    id: int


class BuyModelCallback(CallbackData, prefix='buy-model'):
    avatar_id: int
    level: int = 1


class PromocodeCallback(CallbackData, prefix='promocode'):
    type: int