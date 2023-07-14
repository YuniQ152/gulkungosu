import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



def farm_embed(member, farm):
    text = ""
    crop_count = 0

    if len(farm) <= 10:
        for i in range(len(farm)):
            crop = farm[i]
            if crop is not None: # 작물이 심어져 있을 때
                crop_count += 1
                farm[i]['num'] = i+1
                text += generate_crop_text(farm[i], topic="all")
            else:
                text += f"> <:blank:908031851732533318> **작물 없음** ({i+1})\n"

        embed=discord.Embed(title=f"{member.display_name}님의 농장",
                        description=f"🔗 사용하기: </farm:882220435960385547>\n🌱 작물 수: `{crop_count}`/{len(farm)}" + (" \❗" if crop_count != len(farm) else ""),
                        color=discord.Color.blurple())
        
        embed.add_field(name=f"전체 작물", value=text, inline=False)
        return embed

    crop_count = 0   # 밭의 총 작물 수
    harvestable = 0  # 수확 가능
    harvestable_text = ""
    low_health_count = 0
    plowable_count = 0 # 밭 갈기 가능
    waterable_count = 0 # 물 주기 가능

    for i in range(len(farm)):
        crop = farm[i]
        if crop is not None: # 작물이 심어져 있을 때
            crop_count += 1
            farm[i]['num'] = i+1

            if crop['growth'] == "fruitage": # 작물이 수확 가능한 경우
                harvestable += 1
                harvestable_text += generate_crop_text(farm[i])

            if crop['humidity'] <= 0.9:
                waterable_count += 1

            if crop['fertility'] <= 0.9:
                plowable_count += 1
            
            if crop['health'] < 1: # 작물의 체력이 깎인 경우
                low_health_count += 1

        else:
            harvestable += 1
            harvestable_text += f"> <:blank:908031851732533318> **작물 없음** ({i+1})\n"
            farm[i] = {"staticCropId": "onion",
                       "status": None,
                       "health": 999,
                       "humidity": 999,
                       "fertility": 999,
                       "acceleration": 999,
                       "growth": None} # 수분/비옥도/체력 순으로 정렬할때 오류방지용

    embed=discord.Embed(title=f"{member.display_name}님의 농장",
                        description=f"🔗 사용하기: </farm:882220435960385547>\n🌱 작물 수: `{crop_count}`/{len(farm)}" + (" \❗" if crop_count != len(farm) else ""),
                        color=discord.Color.blurple())

    if harvestable != 0:
        embed.add_field(name=f"✨ 작물 심기/수확: {harvestable}", value=harvestable_text, inline=False)

    severe_count = 0
    if plowable_count != 0:
        fertility_text = ""
        farm = sorted(farm, key=lambda x:x['fertility'])
        if farm[0]['fertility'] >= 0.3: # 가장 비옥도가 낮은 작물이 30% 이상인 경우 (비옥도가 낮아서 위독한 작물이 없는 경우)
            for i in range(min(5, len(farm))):
                fertility_text += generate_crop_text(farm[i], "fertility")
        else:
            for i in range(len(farm)):
                if farm[i]['fertility'] < 0.3:
                    severe_count += 1
                if i < 10:
                    fertility_text += generate_crop_text(farm[i], "fertility")
            if severe_count > 10:
                fertility_text += f"> ❕ 비옥도가 낮은 작물이 `{severe_count - 10}`개 더 있어요"
        embed.add_field(name=f"⚒ 밭 갈기 가능: {plowable_count}", value=fertility_text, inline=False)
    # else:
    #     embed.add_field(name=f"⚒ 밭 갈기 가능", value="> 없음", inline=False)

    severe_count = 0
    if waterable_count != 0:
        humidity_text = ""
        farm = sorted(farm, key=lambda x:x['humidity'])
        if farm[0]['humidity'] >= 0.2:
            for i in range(min(5, len(farm))):
                humidity_text += generate_crop_text(farm[i], "humidity")
        else:
            for i in range(len(farm)):
                if farm[i]['humidity'] < 0.2:
                    severe_count += 1
                if i < 10:
                    humidity_text += generate_crop_text(farm[i], "humidity")
            if severe_count > 10:
                humidity_text += f"> ❕ 수분이 부족한 작물이 `{severe_count - 10}`개 더 있어요"
        embed.add_field(name=f"🚿 물 뿌리기 가능: {waterable_count}", value=humidity_text, inline=False)
    # else:
    #     embed.add_field(name=f"🚿 물 뿌리기 가능", value="> 없음", inline=False)

    severe_count = 0
    if low_health_count != 0:
        health_text = ""
        farm = sorted(farm, key=lambda x:x['health'])
        if farm[0]['health'] >= 0.5:
            for i in range(min(5, len(farm))):
                if farm[i]['health'] == 1.0:
                    break
                health_text += generate_crop_text(farm[i], "health")
        else:
            for i in range(len(farm)):
                if farm[i]['health'] < 0.5:
                    severe_count += 1
                if i < 10:
                    health_text += generate_crop_text(farm[i], "health")
            if severe_count > 10:
                health_text += f"> ❕ 체력이 낮은 작물이 `{severe_count - 10}`개 더 있어요"
        embed.add_field(name=f"🧪 영양제 소비 가능: {low_health_count}", value=health_text, inline=False)
    # else:
    #     embed.add_field(name=f"🧪 영양제 소비 가능", value="> 없음", inline=False)

    return embed


def inventory_embed(member, inv_weight, inv_max_weight, inv_list):
    inv_item_ids = list(i['staticId'] for i in inv_list) # ['1st-anniversary-cake", 1st-anniversary-medal", ...]
    inv_item_ids = list(set(inv_item_ids)) # 리스트 중복제거

    if inv_weight/inv_max_weight <= 0.5:
        embed=discord.Embed(title=f"{member.display_name}님의 인벤토리", description="> 🔗 사용하기: </inventory:882220435847122964>", color=discord.Color.green())
    else:
        color = embed_color(((inv_weight/inv_max_weight)-0.5)*2, reverse=True)
        embed=discord.Embed(title=f"{member.display_name}님의 인벤토리", description="> 🔗 사용하기: </inventory:882220435847122964>", color=discord.Color.from_rgb(color[0], color[1], color[2]))

    items = []
    for i in range(len(inv_item_ids)):
        items.append(fetch_item_one(inv_item_ids[i]))
        items[i]['quantity'] = get_item_quantity_from_inventory(inv_list, inv_item_ids[i])
        items[i]['total_weight'] = items[i]['weight'] * items[i]['quantity']
    items = sorted(items, key=lambda x: (-x['total_weight']))

    description = ""
    for i in range(min(len(items), 15)):
        description += f"{items[i]['icon']} **{items[i]['name_ko']}** × {items[i]['quantity']}개 (무게 {items[i]['total_weight']}) `{items[i]['total_weight']/inv_max_weight*100:.1f}%`\n"
    if len(items) > 15:
        etc_weight_sum = 0

        for i in range(15, len(items)):
            etc_weight_sum = etc_weight_sum + items[i]['total_weight']
        description += f"<:blank:908031851732533318> **기타** (무게 {etc_weight_sum}) `{etc_weight_sum/inv_max_weight*100:.1f}%`\n"
    embed.add_field(name=f"사용 중: {inv_weight} ({(inv_weight/inv_max_weight)*100:.1f}%)", value=description, inline=False)


    if inv_weight <= inv_max_weight:
        embed.add_field(name=f"빈 공간: {inv_max_weight-inv_weight} ({(inv_max_weight-inv_weight)/inv_max_weight*100:.1f}%)", value="", inline=False)


    if inv_weight <= inv_max_weight:
        footer_text = f"⏲ 전체 무게: {inv_weight}/{inv_max_weight}"
    else:
        footer_text = f"⏲ 전체 무게: {inv_weight}/{inv_max_weight} ❗"
    embed.set_footer(text=footer_text)

    return embed


def health_embed(member, user_info, facilities, equipments):
    health = user_info['health'] # 현재 활동력
    max_health = user_info['maxHealth'] # 최대 활동력
    heal_acceleration = user_info['healAcceleration'] # 10분당 회복하는 활동력

    embed=discord.Embed(title=f"💙 {member.display_name}님의 활동력",
                        description=f"**{health:.2f}** / **{max_health:.2f}** (10분당 +{heal_acceleration:.2f})",
                        color=discord.Color(0x5dadec))

    if heal_acceleration != 1:
        health_accel_text = "> <:blank:908031851732533318> **기본** | `🔺1`\n"
        bedroom_accel = 0
        bedroom_count = 0 # 침대 개수
        for facility in facilities:
            if facility['staticId'] == "bedroom" and facility['status'] == "fine": # 시설물이 침대고, 상태가 정상인 경우(공사 중이거나 망가지지 않은 경우)
                bedroom_count += 1
                if   facility['level'] == 1: bedroom_accel += 0.3
                elif facility['level'] == 2: bedroom_accel += 0.6
                elif facility['level'] == 3: bedroom_accel += 1
        if bedroom_accel != 0: # 침대가 주는 활동력 회복량 증가가 0인 경우 (침대가 없거나 공사 중 or 망가짐)
            bedroom_accel = round(bedroom_accel, 3) # 소수점 셋째 자리에서 반올림
            health_accel_text += f"> 🛋 **안방** × {bedroom_count}개 | `{arrow_number(bedroom_accel)}`\n"
        for equipment in equipments:
            if "healAcceleration" in equipment['options']:
                item_info = fetch_item_one(equipment['staticId'])
                health_accel_text += f"> {item_info['icon']} **{item_info['name_ko']}** | `{arrow_number(equipment['options']['healAcceleration'])}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_one(buff)
            if "healAcceleration" in buff_info['options']:
                health_accel_text += f"> {buff_info['icon']} **{buff_info['name_ko']}** | `{arrow_number(buff_info['options']['healAcceleration'])}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name="활동력 회복량 증가", value=health_accel_text)

    if max_health != 100:
        max_health_text = "> <:blank:908031851732533318> **기본** | `🔺100`\n"
        for equipment in equipments:
            if "maxHealth" in equipment['options']:
                item_info = fetch_item_one(equipment['staticId'])
                max_health_text += f"> {item_info['icon']} **{item_info['name_ko']}** | `{arrow_number(equipment['options']['maxHealth'])}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_one(buff)
            if "maxHealth" in buff_info['options']:
                max_health_text += f"> {buff_info['icon']} **{buff_info['name_ko']}** | `{arrow_number(buff_info['options']['maxHealth'])}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name="최대 활동력 증가", value=max_health_text)
        
    return embed


def stats_embed(user, user_info, target = None, target_info = None):
    if target is None: # 타겟이 없는 경우
        embed=discord.Embed(title=f"{user.display_name}님의 능력치", description="", color=discord.Color(0xe67e22))
        embed.add_field(name="물리 공격력", value=user_info['stats']['pf'])
        embed.add_field(name="마법 공격력", value=user_info['stats']['mf'])
        embed.add_field(name="기동력",      value=user_info['stats']['speed'])
        embed.add_field(name="물리 방어력", value=user_info['stats']['pr'])
        embed.add_field(name="마법 방어력", value=user_info['stats']['mr'])
        embed.add_field(name="집중력",      value=user_info['stats']['concentration'])
        return embed
    else: # 타겟이 있는 경우
        stats = ["물리 공격력", "물리 방어력", "마법 공격력", "마법 방어력", "기동력", "집중력"]
        embed_user_field_value = ""
        user_stats = [user_info['stats']['pf'],
                      user_info['stats']['pr'],
                      user_info['stats']['mf'],
                      user_info['stats']['mr'],
                      user_info['stats']['speed'],
                      user_info['stats']['concentration']]
        embed_target_field_value = ""
        target_stats = [target_info['stats']['pf'],
                        target_info['stats']['pr'],
                        target_info['stats']['mf'],
                        target_info['stats']['mr'],
                        target_info['stats']['speed'],
                        target_info['stats']['concentration']]
        compare_field_value = ""

        for i in range(6):
            embed_user_field_value += f"{stats[i]}: {user_stats[i]}\n"
            if user_stats[i] - target_stats[i] > 0:
                compare_field_value += f"`◀ {user_stats[i]-target_stats[i]}`\n"
            elif user_stats[i] - target_stats[i] < 0:
                compare_field_value += f"`{target_stats[i]-user_stats[i]} ▶`\n"
            else:
                compare_field_value += "`-`\n"
            embed_target_field_value += f"{stats[i]}: {target_stats[i]}\n"
            

        embed=discord.Embed(title=f"{user.display_name} vs {target.display_name} 능력치 비교", description="", color=discord.Color(0xe67e22))
        embed.add_field(name=user.display_name, value=embed_user_field_value)
        embed.add_field(name="vs", value=compare_field_value)
        embed.add_field(name=target.display_name, value=embed_target_field_value)
        return embed


def agora_embed(member: discord.Member, inv_list: list) -> discord.Embed:
    expired_list = []

    for item in inv_list:
        if item['staticId'] == "ticket-agora":
            if "expiredAt" in item:
                expired_list.append(int(item['expiredAt']/1000))
            else:
                expired_list.append(9999999999)

    text = ""
    expired_list.sort()
    for ticket in expired_list:
        if ticket == 9999999999:
            break
        text += f"<t:{ticket}:f> (<t:{ticket}:R>)\n"
    interminable = expired_list.count(9999999999) # 무기한 입장권 개수
    if interminable != 0:
        text += f"무기한 광장 입장권 {interminable}개"

    embed=discord.Embed(
        title=f"{member.display_name}님의 광장 입장권",
        description=f"> 🔗 사용하기: </agora:910495388300091392>\n> 🎟️ 입장권 개수: {len(expired_list)}",
        color=discord.Color(0xbe1931)
    )
    embed.add_field(name="만료일", value=text)

    return embed


def land_embed(member: discord.Member, size: list, facilities: list) -> discord.Embed:
    def facility_status(status):
        """
        스탯을 이모지로 반환합니다.
        fine -> ✅
        working -> ⚡
        underConstruction -> 🚧
        broken -> ❎
        """
        if status == "fine":
            return "✅"
        elif status == "working":
            return "⚡"
        elif status == "underConstruction":
            return "🚧"
        elif status == "broken":
            return "❎"
        else:
            raise Exception("알 수 없는 상태")
        
    embed=discord.Embed(title=f"🗺️ {member.display_name}님의 영토",
                        description=f"> 📐 크기: {size[0]}×{size[1]}",
                        color=discord.Color(0x5dadec))
    
    facilities_text = ""

    facilities = sorted(facilities, key=lambda x: x['health'])
    
    for facility in facilities[:15]:
        facility_info = fetch_facility_one(facility['staticId'])
        facilities_text += f"> **[{number_to_alphabet(facility['position'][0] + 1, True)}{facility['position'][1] + 1}]** {facility_info['icon']} **{facility_info['name_ko']}** {'⭐' * facility['level']} | {facility['health']*100:.2f}% | {facility_status(facility['status'])}\n"

    embed.add_field(name="시설물 목록 (최대 15개)", value=facilities_text, inline=False)
    embed.set_footer(text="시설물 위치는 왼쪽 위 모서리를 기준으로 하기 때문에 파머모에서 나타나는 것과 다를 수 있습니다.")

    return embed


class User(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="농장", callback=self.farm_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="인벤토리", callback=self.inventory_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="활동력", callback=self.health_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="능력치", callback=self.stats_contextmenu))
        # self.bot.tree.add_command(app_commands.ContextMenu(name="광장 입장권", callback=self.agora_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="영토", callback=self.land_contextmenu))



    @commands.hybrid_command(name="농장",
                             aliases=['farm', '팜', 'ㄴㅈ', 'ㄵ', 'ㅍ', 'shdwkd', 'vka', 'sw', 'v'],
                             description="농장의 정보를 확인합니다.",
                             usage="(사용자)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="농장을 조회할 대상. 입력하지 않을 경우 본인을 조회합니다.")
    async def farm(self, ctx: commands.Context, *, member: discord.Member = None):
        """사용자의 농장 정보를 확인하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다.
        개간된 밭이 10개 이하라면 모든 작물을 보여줍니다. 개간된 밭이 10개 이상이라면 가장 수분이 낮은 작물과 가장 비옥도가 낮은 작물을 5개씩 보여줍니다. 체력이 감소된 작물이 있다면 그 작물도 보여줍니다. 만약에 특별히 위독한 작물이 있다면 해당 작물을 추가로 보여줍니다."""

        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author

        response_code, user_id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, farm = get_user_farm(user_id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        embed = farm_embed(member, farm)
        await ctx.reply(embed=embed)
    async def farm_contextmenu(self, interaction: Interaction, member: discord.Member):
        response_code, user_id = get_user_id(interaction.guild.id, member.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, farm = get_user_farm(user_id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return

        embed = farm_embed(member, farm)
        await interaction.response.send_message(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="인벤토리",
                             aliases=['inventory', 'inv', '인벤', '인', 'ㅇㅂㅌㄹ', 'ㅇㅂ', 'ㅇ', 'dlsqpsxhfl', 'dlsqps', 'dls', 'dqxf', 'dq', 'd'],
                             description="인벤토리의 아이템이 얼마나 무게를 차지하는지 확인합니다.",
                             usage="(사용자)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="인벤토리를 조회할 대상. 입력하지 않을 경우 본인을 조회합니다.")
    async def inventory(self, ctx: commands.Context, *, member: discord.Member = None):
        """사용자의 인벤토리를 조회하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다.
        인벤토리에 사용하고 있는 무게와 남아있는 무게를 보여주고, 어떤 아이템이 무게를 가장 많이 차지하는지 최대 15개까지 보여줍니다. 색상은 차지하는 무게가 50% ~ 100%일 때 무게에 따라 초록색, 노란색, 빨간색으로 나타며 그 이하일 경우 초록색, 그 이상일 경우 빨간색으로 나타납니다."""
        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author
        response_code, user_id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, inv_weight, inv_max_weight, inv_list = get_user_inventory(user_id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        embed = inventory_embed(member, inv_weight, inv_max_weight, inv_list)
        await ctx.reply(embed=embed)
    async def inventory_contextmenu(self, interaction: Interaction, member: discord.Member):
        response_code, user_id = get_user_id(interaction.guild.id, member.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, inv_weight, inv_max_weight, inv_list = get_user_inventory(user_id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return

        embed = inventory_embed(member, inv_weight, inv_max_weight, inv_list)
        await interaction.response.send_message(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="활동력",
                             aliases=['health', '활', 'ㅎㄷㄹ', 'ㅎ', 'ghkfehdfur', 'ghkf', 'gef', 'g'],
                             description="현재 활동력과 10분당 회복하는 활동력을 보여줍니다.",
                             usage="(사용자)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="활동력 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.")
    async def health(self, ctx: commands.Context, *, member: discord.Member = None):
        """활동력 정보를 확인하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다.
        현재 활동력과 최대 활동력, 10분당 활동력 회복량을 보여주고 이를 증가시키는 시설물이나 장비, 버프를 보여줍니다."""
        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author

        response_code, id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, size, facilities = get_user_land(id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, equipments = get_user_equipment(id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        embed = health_embed(member, user_info, facilities, equipments)
        await ctx.reply(embed=embed, ephemeral=True)
    async def health_contextmenu(self, interaction: Interaction, member: discord.Member):
        response_code, id = get_user_id(interaction.guild.id, member.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, size, facilities = get_user_land(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, equipments = get_user_equipment(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return

        embed = health_embed(member, user_info, facilities, equipments)
        await interaction.response.send_message(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="능력치",
                             aliases=['stats', '능력', 'ㄴㄹㅊ', 'ㄴㄹ', 'smdfurcl', 'smdfur', 'sfc', 'sf'],
                             description="현재 능력치를 보여줍니다.",
                             usage="(사용자) (비교 대상)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="능력치 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.", target="능력치 정보를 비교할 대상.")
    async def stats(self, ctx: commands.Context, *, member: discord.Member = None, target: discord.Member = None):
        """능력치 정보를 확인하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다. `(비교 대상)`은 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 비교 대상은 없습니다.
        `(비교 대상)`이 없을 때: `(사용자)`의 능력치를 보여줍니다.
        `(비교 대상)`이 있을 때: `(사용자)`와 `(비교 대상)`의 능력치를 보여주고 각 능력치별로 어느 쪽의 능력치가 얼마나 높은지 보여줍니다.
        *(능력치에는 물리 공격력, 물리 방어력, 마법 공격력, 마법 방어력, 기동력, 집중력이 있습니다.)*"""
        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author

        response_code, id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        if target is not None and member != target:
            response_code, id = get_user_id(ctx.guild.id, target.id)
            if response_code != 200: await ctx.reply(api_error_message(response_code, target), ephemeral=True); return
            response_code, target_info = get_user_info(id)
            if response_code != 200: await ctx.reply(api_error_message(response_code, target), ephemeral=True); return

            embed = stats_embed(member, user_info, target, target_info)
        else:
            embed = stats_embed(member, user_info)

        await ctx.reply(embed=embed, ephemeral=True)
    async def stats_contextmenu(self, interaction: Interaction, target: discord.Member):
        response_code, id = get_user_id(interaction.guild.id, interaction.user.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return

        if interaction.user != target: # 자기 자신의 능력치를 조회하지 않는 경우 (타겟이 있는 경우)
            response_code, id = get_user_id(interaction.guild.id, target.id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return
            response_code, target_info = get_user_info(id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return

            embed = stats_embed(interaction.user, user_info, target, target_info)
        else: # 자기자신 (타겟이 없는 경우)
            embed = stats_embed(interaction.user, user_info)

        await interaction.response.send_message(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="광장입장권",
                             aliases=['agora_ticket', 'agoraticket', 'ㄱㅈㅇㅈㄱ', '광장', 'ㄱㅈ', '입장권', 'ㅇㅈㄱ', 'rwdwr', 'rhkdwkd', 'rw', 'dlqwkdrnjs', 'dwr'],
                             description="광장 입장권의 개수와 만료일 확인합니다.",
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="광장 입장권 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.")
    async def agora_ticket(self, ctx: commands.Context, *, member: discord.Member = None):
        """광장 입장권의 개수와 만료일 확인하는 명령어입니다.
        만료일이 따로 없을 경우 "무기한"으로 나타납니다."""

        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author
        response_code, user_id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, inv_weight, inv_max_weight, inv_list = get_user_inventory(user_id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        embed = agora_embed(member, inv_list)

        await ctx.reply(embed=embed, ephemeral=True)
    # async def agora_contextmenu(self, interaction: Interaction, member: discord.Member):
    #     response_code, user_id = get_user_id(interaction.guild.id, member.id)
    #     if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
    #     response_code, inv_weight, inv_max_weight, inv_list = get_user_inventory(user_id)
    #     if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return

    #     embed = agora_embed(member, inv_list)
    #     await interaction.response.send_message(embed=embed, ephemeral=True)



    @commands.hybrid_command(name="영토",
                             aliases=['land', '땅', 'ㅇㅌ', 'ㄸ', 'ㄷㄷ', 'Ekd', 'dx', 'E', 'ee'],
                             description="보유한 시설물을 보여줍니다.",
                             usage="(사용자)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="보유한 시설물을 조회할 대상. 입력하지 않을 경우 본인이 조회됨.")
    async def land(self, ctx: commands.Context, *, member: discord.Member = None):
        """
        보유한 시설물을 확인하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다.
        시설물을 내구도 오름차순으로 정렬하고 망가진 시설물의 경우 특별히 강조 표시합니다.
        """
        if member is None:
            member = ctx.message.author
        response_code, user_id = get_user_id(ctx.guild.id, member.id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return
        response_code, size, facilities = get_user_land(user_id)
        if response_code != 200: await ctx.reply(api_error_message(response_code, member), ephemeral=True); return

        embed = land_embed(member, size, facilities)
        await ctx.reply(embed=embed, ephemeral=True)
    async def land_contextmenu(self, interaction: Interaction, member: discord.Member):
        response_code, user_id = get_user_id(interaction.guild.id, member.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return
        response_code, size, facilities = get_user_land(user_id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, member), ephemeral=True); return

        embed = land_embed(member, size, facilities)
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))