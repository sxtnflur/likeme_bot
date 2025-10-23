import os.path
from pathlib import Path
import re

from .base import BaseStorage
from ..s3 import FilesManagerS3


class S3FileStorage(BaseStorage):
    def __init__(self,
                 s3_manager: FilesManagerS3,
                 base_url: str
                 ):
        self.manager = s3_manager
        super(S3FileStorage, self).__init__(base_url=base_url)

    async def _on_start_transaction(self) -> None:
        await self.manager.__aenter__()

    async def _on_close_transaction(self, exc: Exception | None = None) -> None:
        if exc is None:
            await self.manager.__aexit__(None, None, None)
        else:
            await self.manager.__aexit__(type(exc), exc, exc.__traceback__)

    def file_path_to_key(self, file_path: Path) -> str:
        file_path = file_path.__str__().replace('\\', '/')
        file_path = re.sub(r'^/+', '/', file_path)
        if file_path.startswith('/'):
            file_path = file_path[1:]
        print(f'{file_path=}')
        return file_path

    async def _save_file_get_url(self, file: bytes, file_path: Path) -> None:
        await self.manager.set(key=self.file_path_to_key(file_path), file=file)

    async def _delete_file(self, file_path: Path) -> None:
        await self.manager.delete(key=self.file_path_to_key(file_path))