import os.path
import time
from pathlib import Path

import aiofiles
from .base import BaseStorage


class FileStorage(BaseStorage):
    def __init__(self, base_url: str, base_path: str):
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)

        super().__init__(base_url, base_path)

    def get_file_path(self, filename: str, folder: str | None = None) -> Path:
        path = Path(self.base_path)
        if folder:
            if folder.startswith('/'):
                folder = folder[1:]
            path = path.joinpath(folder)

        if '.' not in path.__str__() and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path.joinpath(filename)

    async def _save_file_get_url(self, file: bytes, file_path: Path) -> None:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file)

    async def _delete_file(self, file_path: Path) -> None:
        os.remove(file_path)