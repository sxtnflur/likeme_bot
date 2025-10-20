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
    API_PREFIX: str = '/api/v1'
    BOT_WEBHOOK_ENDPOINT: str = '/webhook'
    BOT_URL: str

    FILES_PATH: str = '/home/cdn/leekai'
    FILES_BASE_URL: str


settings = Settings(_env_file='.env')
