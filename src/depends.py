from bot.loader import bot
from config import settings
from openai import AsyncOpenAI
from payments import YooKassaService, PaymentFactory
from services.ai.image_generator import ImageGeneratorService
from services.ai.openai_service import OpenAIService
from services.avatars_service import AvatarsService
from services.payment import PaymentService
from services.storage import BaseStorage, FileStorage
from services.users import UsersService

if settings.PAYMENT_TEST:
    yookassa_service = YooKassaService(
        shop_id=settings.YOOKASSA_SHOP_ID_TEST,
        api_token=settings.YOOKASSA_API_KEY_TEST
    )
else:
    yookassa_service = YooKassaService(
        shop_id=settings.YOOKASSA_SHOP_ID,
        api_token=settings.YOOKASSA_API_KEY
    )

payment_factory = PaymentFactory(
    yookassa=yookassa_service
)

files_storage: BaseStorage = FileStorage(
    path=settings.FILES_PATH, base_url=settings.FILES_BASE_URL
)

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

openai_service = OpenAIService(
    openai_client=openai_client,
    default_model='gpt-4.1',
    default_max_tokens=2000
)

image_generator_service = ImageGeneratorService(bot=bot, file_storage=files_storage)


avatars_service = AvatarsService(bot=bot, storage=files_storage)


payments_service = PaymentService(bot=bot)

users_service = UsersService(bot=bot, storage=files_storage)