import sqlite3
from abc import ABC, abstractmethod
from io import BytesIO
from sqlite3 import Cursor
from typing import Dict, List

from khl import Bot

import utils
from configuration import JsonConfiguration


class FairySoulStorage(ABC):
    _bot: Bot

    def __init__(self, bot: Bot):
        self._bot = bot

    @abstractmethod
    async def load_picture(self, key: str, default_url: str):
        pass

    @property
    def bot(self):
        return self._bot


class FairySoulJsonStorage(FairySoulStorage):
    _json: JsonConfiguration

    def __init__(self, bot: Bot, file: str):
        super().__init__(bot)
        self._json = JsonConfiguration(file)

    async def load_picture(self, key: str, default_url: str):
        if not self._json.contains(key):
            self._json.set(key,
                           await self.bot.client.create_asset(BytesIO(await utils.fetch_url_bytes(default_url))))
            self._json.save()
        return self._json.get(key)


class FairySoulSqliteStorage(FairySoulStorage):
    _file: str
    _cache: Dict[str, str] = dict()
    _keys: List[str] = list()

    def __init__(self, bot: Bot, file: str):
        super().__init__(bot)
        self._file = file
        connection = sqlite3.connect(self._file)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS `fairy_soul_pics` "
                       "('PIC_KEY' TEXT NOT NULL, 'PIC_URL' TEXT NOT NULL);")
        connection.commit()
        self._load_cache(cursor)
        connection.close()

    async def load_picture(self, key: str, default_url: str, force_update: bool = False):
        if (key not in self._cache and key not in self._keys) or force_update:
            url = await self.bot.client.create_asset(BytesIO(await utils.fetch_url_bytes(default_url)))
            connection = sqlite3.connect(self._file)
            cursor = connection.cursor()
            cursor.execute(
                "REPLACE INTO `fairy_soul_pics` (PIC_KEY, PIC_URL) VALUES (?, ?);",
                (key, url))
            connection.commit()
            connection.close()
            self._cache[key] = url
            self._keys.append(key)
        else:
            if key not in self._cache:
                connection = sqlite3.connect(self._file)
                cursor = connection.cursor()
                cc = cursor.execute(f"SELECT PIC_KEY, PIC_URL from `fairy_soul_pics` WHERE PIC_KEY={key};")
                cc.next()
                for row in cc:
                    self._cache[row[0]] = row[1]
                    break
        result = self._cache[key]
        if len(self._cache) > 1024:  # prevent out of memory
            self._cache.clear()
        return result

    def _load_cache(self, cursor: Cursor):
        cc = cursor.execute("SELECT PIC_KEY, PIC_URL from `fairy_soul_pics`;")
        for row in cc:
            if len(self._cache) >= 512:  # Only cache 512 of the pics
                break
            self._cache[row[0]] = row[1]
            self._keys.append(row[0])
