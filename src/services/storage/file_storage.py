import os.path
import time
from pathlib import Path

import aiofiles
from .base import BaseStorage


class FileStorage(BaseStorage):
    def __init__(self, path: str, base_url: str):
        self.path = path
        self.base_url = base_url

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def get_file_path(self, filename: str, folder: str | None = None) -> Path:
        path = Path(self.path)
        print(f'{path=}')
        if folder:
            if folder.startswith('/'):
                folder = folder[1:]
            path = path.joinpath(folder)

        print(f'{path=}')
        if '.' not in path.__str__() and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        print(f'{path=}')
        print(f'{filename=}')
        return path.joinpath(filename)

    def create_url(self, filename: str, folder: str | None = None) -> str:
        url = self.base_url
        if folder:
            if not folder.startswith('/'):
                folder = '/' + folder
            if folder.endswith('/'):
                folder = folder[:-1]
            url += folder
        if filename.startswith('/'):
            filename = filename[1:]
        return url + '/' + filename

    async def save_file_get_url(self, file: bytes, filename: str | None = None,
                                folder: str | None = None,
                                replace_by_file_path: bool = False) -> str:
        filename = '-'.join(filename.split())
        print(f'{replace_by_file_path=}')
        if not replace_by_file_path:
            filename = f'{round(time.time())}_' + filename
        file_path = self.get_file_path(filename, folder)
        print(f'{file_path=}')
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file)

        return self.create_url(filename, folder)

    async def delete_file(self, filename: str | None = None, folder: str | None = None) -> None:
        file_path = self.get_file_path(filename, folder)
        os.remove(file_path)