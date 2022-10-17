from typing import Union

from aiohttp import ClientSession, TCPConnector


async def fetch_uuid(player_name: str) -> Union[str, None]:
    async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
        async with session.get(f'https://api.minetools.eu/uuid/{player_name}', verify_ssl=False) as response:
            if response.status == 200:
                response = await response.json()
                if response['status'] == "OK":
                    return response['id']
    return None


async def fetch_long_uuid(player_name: str) -> Union[str, None]:
    uuid = await fetch_uuid(player_name)
    return uuid if uuid is None else f'{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:32]}'
