import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



class Log(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.hybrid_command(name="test",
                             aliases=['t', 'ㅅ'],
                             description="테스트용커맨드",
                             with_app_command=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def test(self, ctx: commands.Context):
        embed=discord.Embed(title=":mountain_snow: YuniQ 님의 갱", description=":information_source: 아래 맵의 버튼 중 하나를 클릭하면 :strawberry: 10개를 소비하고 지하 1층부터 채굴을 시작합니다.\n시작한지 1시간이 지나면 그동안 모은 채굴 보상을 획득하고 맵이 초기화됩니다.")
        await ctx.reply(embed=embed)



    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.embeds) != 0 and (message.author.id == 870304475326332968 or message.author.id == 1055865319467520140):
            embed = message.embeds[0]
            if "님의 갱" in embed.title or "'s Pit" in embed.title:
                print(embed.title)
                # await message.channel.send("갱감지")



    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        pass



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Log(bot))