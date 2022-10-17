from khl import Bot, Message, EventTypes, Event, PublicTextChannel

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
            await kook_bot.send(PublicTextChannel(_gate_=kook_bot.client.gate,
                                                  id=channel_id),
                                await messages.skyblock_stats_info(kook_bot, storage, player, profile))
        elif value.startswith('mayor_'):
            mayor_name = value[6:]
            election_data = await hypixel_client.fetch_election()
            for mayor in election_data['current']['candidates']:
                if mayor['name'] == mayor_name:
                    await kook_bot.send(PublicTextChannel(_gate_=kook_bot.client.gate,
                                                          id=channel_id),
                                        messages.skyblock_stats_election_single_mayor(mayor))
                    break
            ...


if __name__ == '__main__':
    main()
