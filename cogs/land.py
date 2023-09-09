import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



def land_embed(member: discord.Member, size: list, facilities: list) -> discord.Embed:
    def facility_status(status):
        """
        스탯을 이모지로 반환합니다.
        fine -> ✅
        working -> ⚡
        underConstruction -> 🚧
        broken -> ❌
        """
        if status == "fine":
            return "✅"
        elif status == "working":
            return "⚡"
        elif status == "underConstruction":
            return "🚧"
        elif status == "broken":
            return "❌"
        else:
            raise Exception("알 수 없는 상태")
        
    embed=discord.Embed(title=f"🗺️ {member.display_name}님의 영토",
                        description=f"> 🔗 사용하기: </land:882220435842949170>\n> 📐 크기: {size[0]}×{size[1]}",
                        color=discord.Color(0x5dadec))
    
    facilities_text = ""

    facilities = sorted(facilities, key=lambda x: x['health'])
    
    for facility in facilities[:15]:
        facility_info = fetch_facility_one(facility['staticId'])
        facilities_text += f"> **[{number_to_alphabet(facility['position'][0] + 1, True)}{facility['position'][1] + 1}]** {facility_info['icon']} **{facility_info['name']}** {'⭐' * facility['level']} | {facility['health']*100:.2f}% | {facility_status(facility['status'])}\n"

    embed.add_field(name="시설물 목록 (최대 15개)", value=facilities_text, inline=False)
    embed.set_footer(text="시설물 위치는 왼쪽 위 모서리를 기준으로 하기 때문에 파머모에서 나타나는 것과 다를 수 있습니다.")

    return embed


class Land(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="영토", callback=self.land_contextmenu))


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
    await bot.add_cog(Land(bot))
    