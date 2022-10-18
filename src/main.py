import logging

from aiohttp import ClientSession
from khl import Bot, Message, EventTypes, Event, PublicTextChannel, api, User

from configuration import JsonConfiguration
from hypixel import HypixelClient
from storage import FairySoulSqliteStorage

import messages
import utils
import minecraft

config = JsonConfiguration("data/config.json")

kook_bot = Bot(token=utils.require(config, 'kook_token', 'Token is missed'))
hypixel_client = HypixelClient(api_key=utils.require(config, 'hypixel-api-token', 'Hypixel API Key is missed'))

storage = FairySoulSqliteStorage(kook_bot, 'data/fairy_soul.db')


def main():
    kook_bot.run()
    ...


class _KookGuild:
    name: str
    id: str
    master_name: str
    master_id: str
    user_count: int

    def __init__(self, data1: dict, data2: User, data3: dict):
        self.name = data1['name']
        self.id = data1['id']
        self.master_name = data2.username
        self.master_id = data2.id
        self.user_count = data3['user_count']


@kook_bot.command(name="admin", prefixes=[".", "/", "。"])
async def admin_command(msg: Message, *args):
    if msg.author_id != "982587531":
        return
    if len(args) == 1:
        operation = str(args[0]).lower()
        if operation == 'joined':
            guilds = await kook_bot.client.gate.exec_pagination_req(api.Guild.list())
            kook_guilds = list()
            for guild in guilds:
                users_info = await kook_bot.client.gate.exec_req(api.Guild.userList(guild_id=guild['id']))
                master = await kook_bot.fetch_user(guild['master_id'])
                kook_guilds.append(_KookGuild(guild, master, users_info))
            joined = "---\n"
            length = len(kook_guilds)
            for i in range(length):
                guild = kook_guilds[i]
                joined += f"服务器: {guild.name}({guild.id})"
                joined += f"服主: {guild.master_name}({guild.master_id})"
                joined += f"人数: {guild.user_count}"
                joined += "---\n"

            await msg.reply(joined)


@kook_bot.command(prefixes=['/', '.', '。'], name='skyblock', aliases=['sb'])
async def skyblock_command(msg: Message, *args):
    if len(args) == 1:
        if not await utils.require_str(args[0], msg):
            return
        arg0 = args[0].lower()
        if arg0 == 'help':
            await msg.reply(messages.skyblock_help())
        elif arg0 == 'election':
            await msg.reply(await messages.skyblock_stats_election(kook_bot, hypixel_client, storage))
        else:
            await msg.reply(messages.skyblock_gotohelp(msg.author))
    elif len(args) == 2:
        if not await utils.require_str(args[0], msg):
            return
        arg0 = args[0].lower()
        if arg0 == 'find':
            if not await utils.require_str(args[1], msg):
                return
            player_name = args[1]
            uuid = await minecraft.fetch_long_uuid(player_name)
            if uuid is None:
                await msg.reply(messages.player_not_exists(msg.author))
                return
            player = await hypixel_client.fetch_player_info(uuid=uuid)
            skyblock_data = await hypixel_client.fetch_skyblock_profiles(uuid)
            await msg.reply(await messages.skyblock_stats_find(kook_bot, storage, player, skyblock_data))
            ...
        else:
            await msg.reply(messages.skyblock_gotohelp(msg.author))
    else:
        await msg.reply(messages.skyblock_gotohelp(msg.author))
    ...


@kook_bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def button_clicked(b: Bot, event: Event):
    value = str(event.extra['body']['value'])
    channel_id = event.extra['body']['target_id']
    if value.startswith('fairysoul_bot_skyblock_'):
        value = value[23:]
        if value.startswith('info_'):
            total_information = value[5:].split("_")
            player = await hypixel_client.fetch_player_info(uuid=total_information[0])
            profile_id = total_information[1]
            profile = await hypixel_client.fetch_skyblock_profile(profile_id)
            await kook_bot.client.send(PublicTextChannel(_gate_=kook_bot.client.gate,
                                                         id=channel_id),
                                       await messages.skyblock_stats_info(kook_bot, storage, player, profile))
        elif value.startswith('mayor_'):
            mayor_name = value[6:]
            election_data = await hypixel_client.fetch_election()
            for mayor in election_data['current']['candidates']:
                if mayor['name'] == mayor_name:
                    await kook_bot.client.send(PublicTextChannel(_gate_=kook_bot.client.gate,
                                                                 id=channel_id),
                                               messages.skyblock_stats_election_single_mayor(mayor))
                    break
            ...


if config.contains('bot-market'):
    @kook_bot.task.add_interval(minutes=29)
    async def task():
        async with ClientSession() as session:
            session.headers.add('uuid', config.get('bot-market'))
            async with session.post("http://bot.gekj.net/api/v1/online.bot") as response:
                logging.debug((await response.json())['msg'])


if __name__ == '__main__':
    main()
