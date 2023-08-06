import discord
from discord import app_commands, Interaction
from discord.ext import commands
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
                text += crop_text(farm[i], topic="all")
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
                harvestable_text += crop_text(farm[i])

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
                fertility_text += crop_text(farm[i], "fertility")
        else:
            for i in range(len(farm)):
                if farm[i]['fertility'] < 0.3:
                    severe_count += 1
                if i < 10:
                    fertility_text += crop_text(farm[i], "fertility")
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
                humidity_text += crop_text(farm[i], "humidity")
        else:
            for i in range(len(farm)):
                if farm[i]['humidity'] < 0.2:
                    severe_count += 1
                if i < 10:
                    humidity_text += crop_text(farm[i], "humidity")
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
                health_text += crop_text(farm[i], "health")
        else:
            for i in range(len(farm)):
                if farm[i]['health'] < 0.5:
                    severe_count += 1
                if i < 10:
                    health_text += crop_text(farm[i], "health")
            if severe_count > 10:
                health_text += f"> ❕ 체력이 낮은 작물이 `{severe_count - 10}`개 더 있어요"
        embed.add_field(name=f"🧪 영양제 소비 가능: {low_health_count}", value=health_text, inline=False)
    # else:
    #     embed.add_field(name=f"🧪 영양제 소비 가능", value="> 없음", inline=False)

    return embed


class Farm(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="농장", callback=self.farm_contextmenu))



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



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Farm(bot))
    