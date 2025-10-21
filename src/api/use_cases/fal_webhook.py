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

    async def on_created_model(self, body: dict) -> None:
        print(f'{body=}')
        request_id: str = str(body['request_id'])
        status: str = body['status']
        diffusers_url = body["payload"]["diffusers_lora_file"]["url"]

        if status != 'OK':
            return

        data = await FalRequestsRepo(db=self.db).get_one(id=request_id)

        model_id = data['model_id']
        print(f'{model_id=}')

        await self.avatars_service.add_modeling_model_to_avatar(
            diffusers_url=diffusers_url,
            model_id=model_id,
            db=self.db
        )

        await FalRequestsRepo(db=self.db).delete(id=request_id)