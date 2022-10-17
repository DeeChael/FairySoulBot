from typing import Union

from aiohttp import ClientSession


async def fetch_uuid(player_name: str) -> Union[str, None]:
    async with ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{player_name}') as response:
            if response.status == 200:
                response = await response.json()
                if 'name' in response and 'id' in response:
                    return response['id']
    return None


async def fetch_long_uuid(player_name: str) -> Union[str, None]:
    uuid = await fetch_uuid(player_name)
    return uuid if uuid is None else f'{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:32]}'
