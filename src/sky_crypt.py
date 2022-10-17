from typing import List

from aiohttp import ClientSession


class Pet:
    uuid: str
    type: str
    exp: float
    active: bool
    tier: str
    # skin
    rarity: str
    level_level: int
    level_xp_current: int
    level_xp_for_next: int
    level_progress: float
    level_xp_max_level: int
    texture_path: str
    lore: str
    display_name: str
    emoji: str


class Profile:
    profile_id: str
    cute_name: str
    current: bool
    pets: List[Pet] = list()
    fairy_exchanges: int

    def __init__(self, data: dict):
        ...


async def get_profile(player_name: str) -> dict:
    async with ClientSession() as session:
        async with session.get(f'https://sky.shiiyu.moe/api/v2/profile/{player_name}') as response:
            if response.status == 200:
                return await response.json()
