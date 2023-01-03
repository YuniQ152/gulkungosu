import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



def generate_crop_text(crop: dict, topic: str = None):
    if crop is not None:
        crop_id      = crop['staticCropId'] # 작물ID
        status       = crop['status']       # 상태: 0 정상 | 1 다갈증 | 2 나쁜 곰팡이 | 3 지렁이
        health       = crop['health']       # 체력
        humidity     = crop['humidity']     # 수분
        fertility    = crop['fertility']    # 비옥도
        acceleration = crop['acceleration'] # 성장 가속
        growth       = crop['growth']       # "dirt" "germination" "maturity" "fruitage"

        if humidity < 0.1 or fertility < 0.15 or health < 0.2:
            crop_text = "> 🚨"
        elif humidity < 0.2 or fertility < 0.3 or health < 0.5:
            crop_text = "> ⚠"
        else:
            crop_text = "> "
        if   growth == "dirt":        crop_text += "🟫"
        elif growth == "germination": crop_text += "🌱"
        elif growth == "maturity":    crop_text += "🌿" if crop_id != "pumpkin" else "🥒"
        elif growth == "fruitage":    crop_text +=f"{fetch_crop_info(crop_id)['icon']}"
        crop_text += f" **{fetch_crop_info(crop_id)['name_ko']}** ({crop['num']})"
        if fertility < 0.3 or topic == "fertility" or status == 2: crop_text +=f" | 🍔 비옥도: `{int(fertility*100)}%`"
        if humidity  < 0.2 or topic == "humidity"  or status == 1: crop_text +=f" | 💧 수분: `{int(humidity*100)}%`"
        if health    < 0.5 or topic == "health"    or status == 2: crop_text +=f" | 💚 체력: `{int(health*100)}%`"
        if   status == 1: crop_text += " | 🤒 다갈증"
        elif status == 2: crop_text += " | 🦠 곰팡이"
        elif status == 3: crop_text += " | 🪱 지렁이"
        crop_text += "\n"
    else:
        crop_text = f"> <:blank:908031851732533318> **작물 없음** ({crop['num']})\n"

    return crop_text



def farm_embed(member, farm):
    crop_count = 0   # 밭의 총 작물 수
    harvestable = 0  # 수확 가능
    harvestable_text = ""
    low_health_count = 0
    plowable_count = 0 # 밭 갈기 가능
    waterable_count = 0 # 물 주기 가능

    for i in range(len(farm)):
        crop = farm[i]
        farm[i]['num'] = i+1
        if crop is not None: # 작물이 심어져 있을 때
            crop_count += 1

            if crop['growth'] == "fruitage": # 작물이 수확 가능한 경우
                harvestable += 1
                harvestable_text += generate_crop_text(farm[i])

            if crop['humidity'] < 0.9:
                waterable_count += 1

            if crop['fertility'] < 0.9:
                plowable_count += 1
            
            if crop['health'] < 1: # 작물의 체력이 깎인 경우
                low_health_count += 1

        else:
            harvestable += 1
            harvestable_text += generate_crop_text(farm[i])

    embed=discord.Embed(title=f"{member.name}님의 농장",
                        description=f"🔗 사용하기: </farm:882220435960385547>\n🌱 작물 수: `{crop_count}`/{len(farm)}" + (" \❗" if crop_count != len(farm) else ""),
                        color=discord.Color.blurple())

    if harvestable != 0:
        embed.add_field(name=f"✨ 작물 심기/수확: {harvestable}", value=harvestable_text, inline=False)

    if plowable_count != 0:
        fertility_text = ""
        farm = sorted(farm, key=lambda x:x['fertility'])
        if farm[0]['fertility'] >= 0.3:
            for i in range(min(5, len(farm))):
                if farm[i]['fertility'] == 0.9:
                    break
                fertility_text += generate_crop_text(farm[i], "fertility")
        else:
            fertility_count = 0
            for i in range(len(farm)):
                if farm[i]['fertility'] >= 0.3:
                    break
                fertility_count += 1
                if i <= 10:
                    fertility_text += generate_crop_text(farm[i], "fertility")
            if fertility_count > 10:
                fertility_text += f"> {fertility_count - 10}개의 위독한 작물"
        embed.add_field(name=f"⚒ 비옥도 낮음: {plowable_count}", value=fertility_text, inline=False)
    # else:
    #     embed.add_field(name=f"⚒ 비옥도 낮음", value="> 없음", inline=False)

    if waterable_count != 0:
        humidity_text = ""
        farm = sorted(farm, key=lambda x:x['humidity'])
        if farm[0]['humidity'] >= 0.2:
            for i in range(min(5, len(farm))):
                if farm[i]['humidity'] == 0.9:
                    break
                humidity_text += generate_crop_text(farm[i], "humidity")
        else:
            humidity_count = 0
            for i in range(len(farm)):
                if farm[i]['humidity'] >= 0.2:
                    break
                humidity_count += 1
                if i <= 10:
                    humidity_text += generate_crop_text(farm[i], "humidity")
            if humidity_count > 10:
                humidity_text += f"> {humidity_count - 10}개의 위독한 작물"
        embed.add_field(name=f"🚿 수분 낮음: {waterable_count}", value=humidity_text, inline=False)
    # else:
    #     embed.add_field(name=f"🚿 수분 낮음", value="> 없음", inline=False)

    if low_health_count != 0:
        health_text = ""
        farm = sorted(farm, key=lambda x:x['health'])
        if farm[0]['health'] >= 0.5:
            for i in range(min(5, len(farm))):
                if farm[i]['health'] == 1.0:
                    break
                health_text += generate_crop_text(farm[i], "health")
        else:
            health_count = 0
            for i in range(len(farm)):
                if farm[i]['health'] >= 0.5:
                    break
                health_count += 1
                if i <= 10:
                    health_text += generate_crop_text(farm[i], "health")
            if health_count > 10:
                health_text += f"> {health_count - 10}개의 위독한 작물"
        embed.add_field(name=f"🧪 체력 낮음: {low_health_count}", value=health_text, inline=False)
    # else:
    #     embed.add_field(name=f"🧪 체력 낮음", value="> 없음", inline=False)

    return embed



def inventory_embed(member, inv_weight, inv_max_weight, inv_list):
    inv_item_ids = list(i['staticId'] for i in inv_list) # ['1st-anniversary-cake", 1st-anniversary-medal", ...]
    inv_item_ids = list(set(inv_item_ids)) # 리스트 중복제거

    items = []
    for i in range(len(inv_item_ids)):
        items.append(fetch_item_info(inv_item_ids[i]))
        items[i]['quantity'] = get_item_quantity_from_inventory(inv_list, inv_item_ids[i])
        items[i]['total_weight'] = items[i]['weight'] * items[i]['quantity']
    items = sorted(items, key=lambda x: (-x['total_weight']))

    description = ""
    for i in range(min(len(items), 15)):
        description += f"{items[i]['icon']} **{items[i]['name_ko']}** {items[i]['quantity']}개 (무게 {items[i]['total_weight']} | {items[i]['total_weight']/inv_max_weight*100:.1f}%)\n"
    if len(items) > 15:
        etc_weight_sum = 0

        for i in range(15, len(items)):
            etc_weight_sum = etc_weight_sum + items[i]['total_weight']
        description += f"<:blank:908031851732533318> **기타** (무게 {etc_weight_sum} | {etc_weight_sum/inv_max_weight*100:.1f}%)\n"
    if inv_weight <= inv_max_weight:
        description += f"<:blank:908031851732533318> **빈 공간** (무게 {inv_max_weight-inv_weight} | {(inv_max_weight-inv_weight)/inv_max_weight*100:.1f}%)\n"

    if inv_weight/inv_max_weight <= 0.5:
        embed=discord.Embed(title=f"{member.name}님의 인벤토리 무게 요약", description=description, color=discord.Color.green())
    else:
        color = embed_color(((inv_weight/inv_max_weight)-0.5)*2, reverse=True)
        embed=discord.Embed(title=f"{member.name}님의 인벤토리 무게 요약", description=description, color=discord.Color.from_rgb(color[0], color[1], color[2]))

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

    embed=discord.Embed(title=f"💙 {member.name}님의 활동력",
                        description=f"**{health:.2f}** / **{max_health:.2f}** (10분당 +{heal_acceleration:.2f})",
                        color=discord.Color(0x5dadec))

    if heal_acceleration != 1:
        health_accel_text = "> <:blank:908031851732533318> **기본** | `🔺1`\n"
        bedroom_accel = 0
        bedroom_count = 0
        for facility in facilities:
            if facility['staticId'] == "bedroom" and facility['status'] == "fine":
                bedroom_count += 1
                if   facility['level'] == 1: bedroom_accel += 0.3
                elif facility['level'] == 2: bedroom_accel += 0.6
                elif facility['level'] == 3: bedroom_accel += 1
        if bedroom_accel != 0:
            health_accel_text += f"> 🛋 **안방** × {bedroom_count}개 | `{arrow_number(bedroom_accel)}`\n"
        for equipment in equipments:
            if "healAcceleration" in equipment['options']:
                item_info = fetch_item_info(equipment['staticId'])
                health_accel_text += f"> {item_info['icon']} **{item_info['name_ko']}** | `{arrow_number(equipment['options']['healAcceleration'])}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_info(buff)
            if "healAcceleration" in buff_info['options']:
                health_accel_text += f"> {buff_info['icon']} **{buff_info['name_ko']}** | `{arrow_number(buff_info['options']['healAcceleration'])}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name="활동력 회복량 증가", value=health_accel_text)

    if max_health != 100:
        max_health_text = "> <:blank:908031851732533318> **기본** | `🔺100`\n"
        for equipment in equipments:
            if "maxHealth" in equipment['options']:
                item_info = fetch_item_info(equipment['staticId'])
                max_health_text += f"> {item_info['icon']} **{item_info['name_ko']}** | `{arrow_number(equipment['options']['maxHealth'])}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_info(buff)
            if "maxHealth" in buff_info['options']:
                max_health_text += f"> {buff_info['icon']} **{buff_info['name_ko']}** | `{arrow_number(buff_info['options']['maxHealth'])}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name="최대 활동력 증가", value=max_health_text)
        
    return embed



def stats_embed(user, user_info, target = None, target_info = None):
    if target is None:
        embed=discord.Embed(title=f"{user.name}님의 능력치", description="", color=discord.Color(0xe67e22))
        embed.add_field(name="물리 공격력", value=user_info['stats']['pf'])
        embed.add_field(name="마법 공격력", value=user_info['stats']['mf'])
        embed.add_field(name="기동력", value=user_info['stats']['speed'])
        embed.add_field(name="물리 방어력", value=user_info['stats']['pr'])
        embed.add_field(name="마법 방어력", value=user_info['stats']['mr'])
        embed.add_field(name="집중력", value=user_info['stats']['concentration'])
        return embed
    else:
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
            

        embed=discord.Embed(title=f"{user.name} vs {target.name} 능력치 비교", description="", color=discord.Color(0xe67e22))
        embed.add_field(name=user.name, value=embed_user_field_value)
        embed.add_field(name="vs", value=compare_field_value)
        embed.add_field(name=target.name, value=embed_target_field_value)
        return embed



class User(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="농장", callback=self.farm_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="인벤토리", callback=self.inventory_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="활동력", callback=self.health_contextmenu))
        self.bot.tree.add_command(app_commands.ContextMenu(name="능력치", callback=self.stats_contextmenu))



    @commands.hybrid_command(name="농장",
                             aliases=['farm', '팜', 'ㄴㅈ', 'ㄵ', 'ㅍ', 'shdwkd', 'vka', 'sw', 'v'],
                             description="농장의 정보를 보여줍니다.",
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="농장을 조회할 대상. 입력하지 않을 경우 본인을 조회합니다.")
    async def farm(self, ctx: commands.Context, member: Optional[discord.Member]):
        await ctx.defer(ephemeral = True)
        if member is None: # 대상이 주어지지 않은 경우 본인
            member = ctx.message.author

        response_code, user_id = get_user_id(ctx.guild.id, ctx.author.id)
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
                             description="인벤토리의 아이템이 얼마나 무게를 차지하는지 보여줍니다.",
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="인벤토리를 조회할 대상. 입력하지 않을 경우 본인을 조회합니다.")
    async def inventory(self, ctx: commands.Context, member: Optional[discord.Member]):
        await ctx.defer(ephemeral = True)
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
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="활동력 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.")
    async def health(self, ctx: commands.Context, member: Optional[discord.Member]):
        await ctx.defer(ephemeral = True)
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
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="능력치 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.", target="능력치 정보를 비교할 대상.")
    async def stats(self, ctx: commands.Context, member: Optional[discord.Member], target: Optional[discord.Member] = None):
        await ctx.defer(ephemeral = True)
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
        response_code, id = get_user_id(809809541385682964, interaction.user.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return

        if interaction.user != target: # 자기 자신의 능력치를 조회하지 않는 경우 (타겟이 있는 경우)
            response_code, id = get_user_id(809809541385682964, target.id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return
            response_code, target_info = get_user_info(id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return

            embed = stats_embed(interaction.user, user_info, target, target_info)
        else: # 자기자신 (타겟이 없는 경우)
            embed = stats_embed(interaction.user, user_info)

        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))