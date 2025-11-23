from .start import router as start_router
from .start_messages_chain import router as chain_router
from .avatar import router as avatar_router
from .create_image import router as create_img_router
from .payment import router as pay_router
from .pro_avatar import router as pro_avatar_router
from .unhandled import router as unhandled_router


__routers__ = (
    start_router, chain_router, avatar_router, create_img_router, pay_router,
    pro_avatar_router,

    unhandled_router
)