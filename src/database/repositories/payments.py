from .base import BaseRepo
from ..models.payment import Payment, Order


class OrdersRepo(BaseRepo[Order]):
    model = Order


class PaymentsRepo(BaseRepo[Payment]):
    model = Payment