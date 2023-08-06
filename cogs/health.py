import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



def health_embed(member, user_info, facilities, equipments):
    health = user_info['health'] # 현재 활동력
    max_health = user_info['maxHealth'] # 최대 활동력
    heal_acceleration = user_info['healAcceleration'] # 10분당 회복하는 활동력

    embed=discord.Embed(title=f"💙 {member.display_name}님의 활동력",
                        description=f"**{health:.2f}** / **{max_health}** (10분당 +{heal_acceleration:.2f})",
                        color=discord.Color(0x5dadec))

    if max_health != 100:
        max_health_text = "> <:blank:908031851732533318> **기본** | `🔺100`\n"
        for equipment in equipments:
            if "maxHealth" in equipment['options']:
                item_info = fetch_item_one(equipment['staticId'])
                max_health_text += f"> {item_info['icon']} **{item_info['name']}** | `{arrow_number(equipment['options']['maxHealth'])}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_one(buff)
            if "maxHealth" in buff_info['options']:
                max_health_text += f"> {buff_info['icon']} **{buff_info['name']}** | `{arrow_number(buff_info['options']['maxHealth'])}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name=f"최대 활동력: {max_health}", value=max_health_text)


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
                health_accel_text += f"> {item_info['icon']} **{item_info['name']}** | `{arrow_number(round(equipment['options']['healAcceleration'], 2))}`\n"
        for buff in user_info['buffs']:
            buff_info = fetch_buff_one(buff)
            if "healAcceleration" in buff_info['options']:
                health_accel_text += f"> {buff_info['icon']} **{buff_info['name']}** | `{arrow_number(round(buff_info['options']['healAcceleration'], 2))}` | <t:{int(user_info['buffs'][buff]/1000)}:R>\n"
        embed.add_field(name=f"10분당 활동력 회복량: {heal_acceleration:.2f}", value=health_accel_text)

    return embed



class Health(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="활동력", callback=self.health_contextmenu))


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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Health(bot))
    