from .base import BaseRepo
from ..models.payment import Payment


class PaymentsRepo(BaseRepo[Payment]):
    model = Payment