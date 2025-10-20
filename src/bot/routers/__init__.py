from .start import router as start_router
from .avatar import router as avatar_router
from .create_image import router as create_img_router
from .payment import router as pay_router


__routers__ = (
    start_router, avatar_router, create_img_router, pay_router
)