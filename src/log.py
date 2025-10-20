import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"
)

logger = logging.getLogger('LikeMe.AI')