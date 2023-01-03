import discord
from discord import app_commands, Interaction, Object
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord.app_commands import Choice
from typing import Optional, Literal
from random import randint
from modules.database import *
from modules.get import *
from modules.utils import *



class Server(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.hybrid_command(name="공동농장",
                             aliases=['cofarm', '공팜', 'ㄱㄷㄴㅈ', 'ㄱㄷㄵ', 'ㄱㅍ', 'rhdehdshdwkd', 'rhdvka', 'resw', 'rv'],
                             description="서버의 공동농장 관련 정보를 보여줍니다.",
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def cofarm(self, ctx: commands.Context):
        await ctx.defer(ephemeral = True)

        if ctx.guild.id == 809809541385682964: # 달달소 서버만 예외처리 (가스 너무많이 먹음)
            cofarm_id_list = [809843576094588960, 844551435986665473, 844551361932820550]
        else:
            response_code, cofarm_id_list = get_cofarm_channel_id(ctx.guild.id)
            if response_code != 200: await ctx.reply(api_error_message(response_code), ephemeral=True); return
        
        if len(cofarm_id_list) == 0: # 서버에 공동농장이 없을 때
            await ctx.reply(f"**{ctx.guild.name}**에는 공동농장이 없습니다.")
            return

        embeds = []
        for cofarm_id in cofarm_id_list:
            response_code, farms, contributions = get_cofarm_info(ctx.guild.id, cofarm_id)
            if response_code != 200: await ctx.reply(api_error_message(response_code), ephemeral=True); return

            channel = self.bot.get_channel(cofarm_id)

            plowable  = 0
            waterable = 0
            severe_count = 0
            severe_text = ""
            score = 0
            for crop in farms:

                if crop is not None: # 작물이 심어져 있을 때
                    crop_id      = crop['staticCropId'] # 작물ID
                    status       = crop['status']       # 상태: 0 정상 | 1 다갈증 | 2 나쁜 곰팡이 | 3 지렁이
                    health       = crop['health']       # 체력
                    humidity     = crop['humidity']     # 수분
                    fertility    = crop['fertility']    # 비옥도
                    acceleration = crop['acceleration'] # 성장 가속
                    growth       = crop['growth']       # "dirt" "germination" "maturity" "fruitage"

                    score += (health                              **(3-health)   *0.75 +
                             (fertility if fertility < 0.9 else 1)**(3-fertility)*0.2 +
                             (humidity  if humidity  < 0.9 else 1)**(3-humidity )*0.05
                             ) / len(farms)

                    if fertility < 0.9:
                        plowable += 1
                    if humidity < 0.9:
                        waterable += 1

                    if humidity < 0.2 or fertility < 0.3 or health < 0.5:
                        severe_count += 1
                        if   growth == "dirt":        severe_text += "> 🟫"
                        elif growth == "germination": severe_text += "> 🌱"
                        elif growth == "maturity":    severe_text += "> 🌿" if crop_id != "pumpkin" else "> 🥒"
                        elif growth == "fruitage":    severe_text += f"> {fetch_crop_info(crop_id)['icon']}"
                        severe_text += f" **{fetch_crop_info(crop_id)['name_ko']}**"

                        if fertility < 0.3: severe_text += f" | 🍔 비옥도: `{int(fertility*100)}%`"
                        if humidity < 0.2:  severe_text += f" | 💧 수분: `{int(humidity*100)}%`"
                        if health < 0.5:    severe_text += f" | 💚 체력: `{int(health*100)}%`"
                        if status == 1:     severe_text += " | 🤒 다갈증"
                        if status == 2:     severe_text += " | 🦠 곰팡이"

                        severe_text += "\n"

            crop_count = 0
            for crop in farms:
                if crop is not None:
                    crop_count += 1

            activitible_text=""
            activitible_text += f"> 🚿 **물 뿌리기**: `{waterable}`\n"
            activitible_text += f"> ⚒️ **밭 갈기**: `{plowable}`"

            embed_title = f"{channel.name} 공동농장"
            if cofarm_id != ctx.channel.id:
                description = f">>> 🔗 바로가기: {channel.mention}\n"
            else:
                description = ">>> 🇺🇳 사용하기: </cofarm:886550657916604457>\n"
            description += f"🌱 작물 수: `{crop_count}`/{len(farms)}"
            if crop_count == len(farms): description += "\n"
            else:                        description += " \❗ \n"
            description += f"💯 농장 점수: {int(score*100*2-100)}점"
            color = embed_color(score*2-1)
            embed=discord.Embed(title=embed_title, description=description, color=discord.Color.from_rgb(color[0], color[1], color[2]))
            if plowable != 0 or waterable != 0:
                embed.add_field(name=f"💙 활동력 소비 가능: {waterable*5+plowable*20}", value=activitible_text, inline=False)
            if severe_count != 0:
                embed.add_field(name=f"😵 위독함: {severe_count}곳", value=severe_text, inline=False)

            embeds.append(embed)
        await ctx.reply(embeds=embeds)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))