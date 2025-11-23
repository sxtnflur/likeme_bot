from database import FalRequestsRepo
from services.avatars_service import AvatarsService
from sqlalchemy.ext.asyncio import AsyncSession


class FalWebhookUseCase:
    def __init__(self,
                 db: AsyncSession,
                 avatars_service: AvatarsService,
                 ):
        self.db = db
        self.avatars_service = avatars_service

    async def on_created_model(self, data: dict) -> None:
        print(f'{data=}')
        request_id: str = str(data['request_id'])
        status: str = data['status']
        diffusers_url = data["payload"]["diffusers_lora_file"]["url"]

        if status != 'OK':
            return

        await self.avatars_service.on_trained_portrait_avatar(
            request_id=request_id,
            diffusers_url=diffusers_url,
            db=self.db
        )