from typing import Union

from aiohttp import ClientSession, TCPConnector
from khl import Message, Bot

from configuration import Configuration, MemoryConfiguration


def require(parent: Union[dict, Configuration], key: str, message: str):
    if isinstance(parent, dict):
        parent = MemoryConfiguration(parent)
    if not parent.contains(key):
        raise RuntimeError(message)
    return parent.get(key)


async def emoji(bot: Bot, guild: str, icon: str) -> str:
    guild = await bot.fetch_guild(guild)
    for emoji_dict in (await guild.fetch_emoji_list()):
        if emoji_dict['name'] == icon:
            return f'(emj){emoji_dict["name"]}(emj)[{emoji_dict["id"]}]'
    return ''


async def fetch_url_bytes(url: str) -> bytes:
    async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()


async def require_str(obj, msg: Message) -> bool:
    if not isinstance(obj, str):
        import messages
        await msg.reply(messages.skyblock_gotohelp(msg.author))
        return False
    return True
