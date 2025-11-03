import os
from pathlib import Path

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: str = ''

    DATABASE_URL: str
    TRAIN_CALLBACK_URL: str = ''
    OPENAI_API_KEY: str = ''

    YOOKASSA_SHOP_ID: str
    YOOKASSA_API_KEY: str
    YOOKASSA_SHOP_ID_TEST: str
    YOOKASSA_API_KEY_TEST: str

    PAYMENT_TEST: bool = True

    ENABLE_LANGUAGES: list[str] = ['ru']
    DEFAULT_LANGUAGE: str = 'ru'

    BOT_TOKEN: str
    BOT_WEBHOOK_URL: str | None = None
    BOT_USERNAME: str

    API_PREFIX: str = '/api/v1'
    BOT_WEBHOOK_ENDPOINT: str = '/webhook'
    BOT_URL: str

    FILES_PATH: str = '/home/cdn/leekai'
    FILES_BASE_URL: str

    FAL_KEY: str

    S3_BASE_URL: str
    S3_ENDPOINT: str
    S3_ACCESS: str
    S3_SECRET: str
    S3_BUCKET: str
    S3_REGION_NAME: str = 'ru-7'

    WEBAPP_URL: str
    WEBAPP_DIRECT_URL: str


def get_env_path():
    possible_paths = [
        Path('.env'),
        # Для локальной разработки
        Path(__file__).parent.parent / '.env',
        # Для Docker (если .env копируется в /app)
        Path('/app/.env'),
        # Для случаев когда .env в той же директории
        Path(__file__).parent / '.env',
        # Текущая рабочая директория
        Path.cwd() / '.env',
    ]

    for env_path in possible_paths:
        if env_path.exists():
            print(f"Loaded .env from: {env_path}")
            return env_path
    else:
        print("Warning: .env file not found in any expected location")


settings = Settings(_env_file=get_env_path())


os.environ.setdefault('FAL_KEY', settings.FAL_KEY)