from bot.loader import bot
from config import settings
from openai import AsyncOpenAI
from payments import YooKassaService, PaymentFactory
from services.categories import CategoriesService
from services.image_generator import ImageGeneratorService
from services.ai.openai_service import OpenAIService
from services.avatars_service import AvatarsService
from services.payment import PaymentService
from services.storage import BaseStorage, FileStorage
from services.translation import TranslationService
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
    default_model='gpt-4.1-mini',
    default_max_tokens=2000
)

translation_service = TranslationService(openai=openai_service)

categories_service = CategoriesService(openai=openai_service)

image_generator_service = ImageGeneratorService(bot=bot, file_storage=files_storage,
                                                categories_service=categories_service,
                                                translation_service=translation_service)


avatars_service = AvatarsService(bot=bot, storage=files_storage)

payments_service = PaymentService(bot=bot)

users_service = UsersService(bot=bot, storage=files_storage)
