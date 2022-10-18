import asyncio
import datetime
from typing import Union

from aiohttp import ClientSession, TCPConnector


def _calc_player_level(xp: Union[float, int]) -> float:
    return 1 + (-8750.0 + (8750 ** 2 + 5000 * xp) ** 0.5) / 2500


class Player:
    uuid: str
    name: str
    rank: str
    level: float
    last_login: str

    def __init__(self, data: dict):
        self.uuid = data.get('uuid', '')
        self.name = data.get('displayname', '')
        self.rank = data.get('rank', '')
        self.level = _calc_player_level(data.get('networkExp', 0))
        self.last_login = datetime.datetime.fromtimestamp(float(data.get('lastLogin', 0)) / 1000).strftime(
            "%y-%m-%d %H:%M:%S")
        ...


class SkyblockProfile:
    _id: str
    _cute_name: str
    extra: dict
    selected: bool

    def __init__(self, data: dict):
        self._id = data.get('profile_id', '')
        self._cute_name = data.get('cute_name', '')
        self.selected = data.get('selected', False)
        self.extra = data

    @property
    def id(self):
        return self._id

    @property
    def cute_name(self):
        return self._cute_name


class HypixelClient:
    _lock = asyncio.Lock()
    _session = ClientSession(connector=TCPConnector(verify_ssl=False))

    _headers: dict

    def __init__(self, api_key: str):
        self._headers = {"Api-Key": api_key}

    async def fetch_election(self) -> dict:
        async with self._lock:
            async with self._session.get("https://api.hypixel.net/resources/skyblock/election", headers=self._headers,
                                         timeout=10) as response:
                if response.status == 200:
                    return await response.json()

    async def fetch_player_info(self, uuid: str) -> Player:
        async with self._lock:
            async with self._session.get("https://api.hypixel.net/player", params={'uuid': uuid}, headers=self._headers,
                                         timeout=10) as response:
                if response.status == 200:
                    return Player((await response.json())['player'])

    async def fetch_skyblock_profiles(self, uuid: str) -> SkyblockProfile:
        async with self._lock:
            async with self._session.get("https://api.hypixel.net/skyblock/profiles", params={'uuid': uuid},
                                         headers=self._headers, timeout=10) as response:
                if response.status == 200:
                    for profile in (await response.json())['profiles']:
                        return SkyblockProfile(profile)


    async def fetch_skyblock_profile(self, uuid: str) -> SkyblockProfile:
        async with self._lock:
            async with self._session.get("https://api.hypixel.net/skyblock/profile", params={'profile': uuid},
                                         headers=self._headers, timeout=10) as response:
                if response.status == 200:
                    return SkyblockProfile((await response.json())['profile'])
