from .payment import router as pay_router
from .feed import router as feed_router


__routers__ = (
    pay_router, feed_router
)