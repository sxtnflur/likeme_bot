from aiogram.filters.callback_data import CallbackData


class PaymentStartCallback(CallbackData, prefix='payment'): ...

class BuyImageGenerationsCallback(CallbackData, prefix='buy-image-gens'): ...

class SelectImageGenerationsCallback(CallbackData, prefix='select-image-package'):
    id: int