from typing import Union

from khl import User, Bot
from khl.card import CardMessage, Types, Card, Module, Element, Struct

from hypixel import Player, SkyblockProfile
from storage import FairySoulStorage

import skyblock_utils
import sky_crypt

from hypixel import HypixelClient


def skyblock_help() -> CardMessage:
    return CardMessage(
        Card(
            Module.Header("仙女之魂 | 空岛生存 | 帮助"),
            Module.Section('/skyblock find <玩家名称> - 查询玩家空岛生存的信息\n'
                           '/skyblock election - 查询市长选举信息'),
            Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)),
            theme=Types.Theme.PRIMARY
        )
    )


_MINECRAFT_COLOR_CODES = "0123456789abcdefklmnor"


def _process_minecraft_color(message: str) -> str:
    for code in _MINECRAFT_COLOR_CODES:
        message = message.replace(f'§{code}', '')
    return message


def skyblock_stats_election_single_mayor(mayor_info: dict) -> CardMessage:
    card = Card()
    card.append(Module.Header(f"| 选举 | 竞选者 |"))
    card.append(Module.Divider())
    card.append(Module.Section(
        Element.Text(f'**竞选者名称**: {mayor_info["name"]}\n'
                     '**加成效果:**\n ', type=Types.Text.KMD)
    ))
    perks = mayor_info['perks']
    if len(perks) == 1:
        card.append(Module.Section(
            Element.Text(
                f'**{_process_minecraft_color(perks[0]["name"])}**\n{_process_minecraft_color(perks[0]["description"])}',
                type=Types.Text.KMD)
        ))
    elif len(perks) == 2:
        card.append(Module.Section(
            Struct.Paragraph(
                2,
                Element.Text(
                    f'**{_process_minecraft_color(perks[0]["name"])}**\n{_process_minecraft_color(perks[0]["description"])}',
                    type=Types.Text.KMD),
                Element.Text(
                    f'**{_process_minecraft_color(perks[1]["name"])}**\n{_process_minecraft_color(perks[1]["description"])}',
                    type=Types.Text.KMD)
            )
        ))
    else:
        fields = list()
        for perk in perks:
            fields.append(Element.Text(
                f'**{_process_minecraft_color(perk["name"])}**\n{_process_minecraft_color(perk["description"])}',
                type=Types.Text.KMD))
        card.append(Module.Section(Struct.Paragraph(3, *fields)))
    return CardMessage(card)


async def skyblock_stats_election(bot: Bot, hypixel_client: HypixelClient, storage: FairySoulStorage) -> CardMessage:
    election_data = await hypixel_client.fetch_election()
    card = Card()
    card.append(Module.Header(f"| 选举 |"))
    card.append(Module.Divider())
    card.append(Module.Section(
        Element.Text(f'**本年市长**: {election_data["mayor"]["name"]}\n'
                     '**加成效果:**\n ', type=Types.Text.KMD)
    ))
    perks = election_data['mayor']['perks']
    if len(perks) == 1:
        card.append(Module.Section(
            Element.Text(
                f'**{_process_minecraft_color(perks[0]["name"])}**\n{_process_minecraft_color(perks[0]["description"])}',
                type=Types.Text.KMD)
        ))
    elif len(perks) == 2:
        card.append(Module.Section(
            Struct.Paragraph(
                2,
                Element.Text(
                    f'**{_process_minecraft_color(perks[0]["name"])}**\n{_process_minecraft_color(perks[0]["description"])}',
                    type=Types.Text.KMD),
                Element.Text(
                    f'**{_process_minecraft_color(perks[1]["name"])}**\n{_process_minecraft_color(perks[1]["description"])}',
                    type=Types.Text.KMD)
            )
        ))
    else:
        fields = list()
        for perk in perks:
            fields.append(Element.Text(
                f'**{_process_minecraft_color(perk["name"])}**\n{_process_minecraft_color(perk["description"])}',
                type=Types.Text.KMD))
        card.append(Module.Section(Struct.Paragraph(3, *fields)))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text('**次年市长竞选**', type=Types.Text.KMD)))
    competitors = election_data['current']['candidates']
    total = 0
    for competitor in competitors:
        total += competitor['votes']
    for competitor in competitors:
        card.append(Module.Section(Element.Text(f'{competitor["name"]} - {(competitor["votes"] * 100) // total}% ({competitor["votes"]} 票)'),
                                   mode=Types.SectionMode.RIGHT, accessory=Element.Button(
                '点击查看详细',
                theme=Types.Theme.PRIMARY,
                click=Types.Click.RETURN_VAL,
                value=f'fairysoul_bot_skyblock_mayor_{competitor["name"]}'),
                                   ))
    card.append(Module.Section(Element.Text(f'**总票数**: {total} 票', type=Types.Text.KMD)))
    return CardMessage(card)


async def skyblock_stats_info(bot: Bot, storage: FairySoulStorage, player: Player, profile: SkyblockProfile) -> CardMessage:
    skyblock_data = profile.extra['members'][player.uuid.replace("-", "")]
    sky_crypt_data = await sky_crypt.get_profile(player.name)
    sky_crypt_data = sky_crypt_data['profiles'][profile.id]
    # finding actived pet
    actived_pet = "无宠物"
    for pet in skyblock_data['pets']:
        if pet['active']:
            actived_pet = skyblock_utils.pet_id_to_name(pet['type'])
    card = Card()
    card.append(Module.Header(f"| 基本信息 | {player.name}"))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text('**基础数据**', type=Types.Text.KMD)))
    card.append(Module.Section(
        Struct.Paragraph(
            3,
            Element.Text(f'**❤ 生命值**: {sky_crypt_data["data"]["stats"]["health"]}', type=Types.Text.KMD),
            Element.Text(f'**❈ 防御值**: {sky_crypt_data["data"]["stats"]["defense"]}', type=Types.Text.KMD),
            Element.Text(f'**❁ 力量值**: {sky_crypt_data["data"]["stats"]["strength"]}', type=Types.Text.KMD),
            Element.Text(f'**✦ 速度**: {sky_crypt_data["data"]["stats"]["strength"]}', type=Types.Text.KMD),
            Element.Text(f'**☣ 暴击率**: {sky_crypt_data["data"]["stats"]["crit_chance"]}', type=Types.Text.KMD),
            Element.Text(f'**☠ 暴击伤害**: {sky_crypt_data["data"]["stats"]["crit_damage"]}', type=Types.Text.KMD),
            Element.Text(f'**✎ 智力**: {sky_crypt_data["data"]["stats"]["intelligence"]}', type=Types.Text.KMD),
            Element.Text(f'**⚔ 攻击速度**: {sky_crypt_data["data"]["stats"]["bonus_attack_speed"]}', type=Types.Text.KMD),
            Element.Text(f'**α 海洋生物机率**: {sky_crypt_data["data"]["stats"]["sea_creature_chance"]}',
                         type=Types.Text.KMD),
            Element.Text(f'**✯ 魔力探寻**: {sky_crypt_data["data"]["stats"]["magic_find"]}', type=Types.Text.KMD),
            Element.Text(f'**♣ 宠物幸运**: {sky_crypt_data["data"]["stats"]["pet_luck"]}', type=Types.Text.KMD),
            # Element.Text(f'**❂ 真实防御**: {sky_crypt_data["data"]["stats"]["strength"]}', type=Types.Text.KMD),
            Element.Text(f'**❂ 真实防御**: -1', type=Types.Text.KMD),
            Element.Text(f'**⫽ Ferocity**: {sky_crypt_data["data"]["stats"]["ferocity"]}', type=Types.Text.KMD),
            Element.Text(f'**๑ 技能伤害**: {sky_crypt_data["data"]["stats"]["ability_damage"]}', type=Types.Text.KMD),
            Element.Text(f'**⸕ 采矿速度**: {sky_crypt_data["data"]["stats"]["mining_speed"]}', type=Types.Text.KMD),
            Element.Text(f'**☘ 采矿时运**: {sky_crypt_data["data"]["stats"]["mining_fortune"]}', type=Types.Text.KMD),
            Element.Text(f'**☘ 农业时运**: {sky_crypt_data["data"]["stats"]["farming_fortune"]}', type=Types.Text.KMD),
            Element.Text(f'**☘ 采集时运**: {sky_crypt_data["data"]["stats"]["foraging_fortune"]}', type=Types.Text.KMD),
            Element.Text(f'**✧ Pristine**: {sky_crypt_data["data"]["stats"]["pristine"]}', type=Types.Text.KMD),
            Element.Text(f'**ʬ Soulflow**: {skyblock_data["soulflow"]}', type=Types.Text.KMD),
        )
    ))
    card.append(Module.Divider())
    card.append(
        Module.Section(Element.Text(f'**技能**\n平均等级: {sky_crypt_data["data"]["average_level"]}', type=Types.Text.KMD)))
    card.append(Module.Section(
        Struct.Paragraph(
            3,
            Element.Text(f'**农业**: {sky_crypt_data["data"]["levels"]["farming"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**采矿**: {sky_crypt_data["data"]["levels"]["mining"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**战斗**: {sky_crypt_data["data"]["levels"]["combat"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**采集**: {sky_crypt_data["data"]["levels"]["foraging"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**渔业**: {sky_crypt_data["data"]["levels"]["fishing"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**附魔**: {sky_crypt_data["data"]["levels"]["enchanting"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**炼金**: {sky_crypt_data["data"]["levels"]["alchemy"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**驯养**: {sky_crypt_data["data"]["levels"]["taming"]["level"]}', type=Types.Text.KMD),
            Element.Text(f'**木工**: {sky_crypt_data["data"]["levels"]["carpentry"]["level"]}', type=Types.Text.KMD),
        )
    ))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text(f'**猎手**', type=Types.Text.KMD)))
    card.append(Module.Section(
        Struct.Paragraph(
            3,
            Element.Text(f'**僵尸**: {sky_crypt_data["data"]["slayers"]["zombie"]["level"]["currentLevel"]}',
                         type=Types.Text.KMD),
            Element.Text(f'**蜘蛛**: {sky_crypt_data["data"]["slayers"]["spider"]["level"]["currentLevel"]}',
                         type=Types.Text.KMD),
            Element.Text(f'**狼**: {sky_crypt_data["data"]["slayers"]["wolf"]["level"]["currentLevel"]}',
                         type=Types.Text.KMD),
            Element.Text(f'**末影人**: {sky_crypt_data["data"]["slayers"]["enderman"]["level"]["currentLevel"]}',
                         type=Types.Text.KMD),
            Element.Text(f'**烈焰人**: {sky_crypt_data["data"]["slayers"]["blaze"]["level"]["currentLevel"]}',
                         type=Types.Text.KMD),
        )
    ))
    card.append(Module.Divider())
    card.append(Module.Section(Element.Text('**其他**', type=Types.Text.KMD)))
    card.append(Module.Section(
        Element.Text(f'**当前宠物**: {actived_pet}\n'
                     f'**仙女之魂**: {skyblock_data["fairy_souls_collected"]}\n'
                     f'**最高伤害**: {skyblock_data["stats"]["highest_damage"]}\n'
                     f'**钱包**: {skyblock_data["coin_purse"]}', type=Types.Text.KMD),
    ))
    card.append(Module.Divider())
    card.append(
        Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)))
    return CardMessage(card)


async def skyblock_stats_find(bot: Bot, storage: FairySoulStorage, player: Player,
                              skyblock_data: SkyblockProfile) -> CardMessage:
    uuid = player.uuid
    card = Card()
    card.append(Module.Header(f"| 玩家查询 | {player.name}"))
    card.append(Module.Section(
        text=Element.Text(f'**玩家名称**: {player.name}\n'
                          f'**UUID**: {player.uuid}\n'
                          f'**等级**: {player.level}\n'
                          f'**最后在线**: {player.last_login}\n'
                          f'**当前档案**: {skyblock_data.cute_name}', type=Types.Text.KMD),
        mode=Types.SectionMode.RIGHT,
        accessory=Element.Image(
            await storage.load_picture(f'player_skin_{uuid.replace("-", "")}', f'https://crafatar.com/avatars/{uuid}'))
    ))
    card.append(Module.ActionGroup(
        Element.Button('基本信息',
                       theme=Types.Theme.PRIMARY,
                       click=Types.Click.RETURN_VAL,
                       value=f'fairysoul_bot_skyblock_info_{uuid}_{skyblock_data.id}'),
        Element.Button('敬请期待',
                       theme=Types.Theme.SECONDARY,
                       click=Types.Click.RETURN_VAL,
                       value="coming_soon"
                       # value=f'fairysoul_bot_skyblock_info_{uuid}_{skyblock_data.id}'
                       )
    ))
    card.append(Module.Divider())
    card.append(
        Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)))
    return CardMessage(card)


def skyblock_gotohelp(user: Union[str, User, None] = None) -> CardMessage:
    return failed('输入 /skyblock help 获取帮助', user)


def player_not_exists(user: Union[str, User, None] = None) -> CardMessage:
    return failed('该玩家不存在', user)


def failed(message: str, user: Union[str, User, None] = None) -> CardMessage:
    if isinstance(user, User):
        user = user.id
    card = Card(theme=Types.Theme.DANGER)
    if user is None:
        card.append(Module.Section(Element.Text(message, type=Types.Text.KMD)))
    else:
        card.append(Module.Section(Element.Text(f'(met){user}(met)\n{message}', type=Types.Text.KMD)))
    card.append(
        Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)))
    return CardMessage(card)


def success(message: str, user: Union[str, User, None] = None) -> CardMessage:
    if isinstance(user, User):
        user = user.id
    card = Card(theme=Types.Theme.SUCCESS)
    if user is None:
        card.append(Module.Section(Element.Text(message, type=Types.Text.KMD)))
    else:
        card.append(Module.Section(Element.Text(f'(met){user}(met)\n{message}', type=Types.Text.KMD)))
    card.append(
        Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)))
    return CardMessage(card)


def primary(message: str, user: Union[str, User, None] = None) -> CardMessage:
    if isinstance(user, User):
        user = user.id
    card = Card(theme=Types.Theme.PRIMARY)
    if user is None:
        card.append(Module.Section(Element.Text(message, type=Types.Text.KMD)))
    else:
        card.append(Module.Section(Element.Text(f'(met){user}(met)\n{message}', type=Types.Text.KMD)))
    card.append(
        Module.Context(Element.Text('由 [DeeChael](https://space.bilibili.com/197734515) 开发', type=Types.Text.KMD)))
    return CardMessage(card)
