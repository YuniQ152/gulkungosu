import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.app_commands import Choice, Range
from typing import Literal, Union
from modules.database import *
from modules.get import *
from modules.utils import *


def collection_power_embed(collected):
    exp_multiple = math.floor(1+(collected/60))
    crop_cure = max(0, (collected-60)*(1/12))
    yeast_chance = collected*(1/6) + 10
    recover_health = collected*0.03 + 7
    grow_speed = collected*(1/12) + 120

    description = f"{collected}개의 아이템을 박제했을 때...\n"
    if exp_multiple >= 2: description += f"> <:exp:1037828199679266899> 쓰다듬기로 얻는 경험치가 {exp_multiple}배가 돼요.\n"
    if crop_cure != 0:    description += f"> ⚕️ 아픈 작물을 쓰다듬으면 {crop_cure:.1f}% 확률로 작물이 나아요.\n"
    description += f"> 🧫 곰팡이가 슨 작물을 쓰다듬으면 {yeast_chance:.1f}% 확률로 효모를 얻어요.\n"
    description += f"> 💚 작물을 쓰다듬을 때 잃은 체력의 {recover_health:.1f}%만큼 작물이 회복돼요.\n"
    description += f"> 😁 쓰다듬은 작물이 {grow_speed:.1f}%만큼 빨리 자라게 돼요.\n"

    embed=discord.Embed(title="도감 효과 계산기",
                        description=description,
                        color=discord.Color(0x57f288))
    if 0 <= collected and collected <= 135:
        embed.set_footer(text="이것은 공식을 유추하여 구한 값이에요. 실제 버프 효과와 약간의 차이가 있을 수 있어요.")
    else:
        embed.set_footer(text="실제 파머모에서는 일반 도감에 0 ~ 135개의 아이템만 박제할 수 있어요. 이건 그냥 재미로 봐 주세요.")

    return embed



class Calculator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.hybrid_group(name="계산기",
                           aliases=['ㄱㅅㄱ', 'ㄳㄱ', 'ㄱㄱ', 'rPtksrl', 'rtr', 'rr'],
                           description="파머모 관련 수치를 계산합니다.",
                           with_app_command=True)
    async def calculator(self, ctx: commands.Context):
        """파머모 관련된 계산을 하는 명령어의 그룹입니다. 명령어 그룹 이름 뒤에 공백 한 칸과 하위 명령어 이름으로 하위 명령어를 사용할 수 있습니다.
        예시: `계산기 도감효과`
        하위 명령어의 도움말을 보려면 다음과 같이 할 수 있습니다.
        예시: `도움 계산기 도감효과` 또는 `ㄷㅇ ㄱㅅㄱ ㄷㄱㅎㄱ`"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.calculator)


    @calculator.command(name="도감효과",
                        aliases=['ㄷㄱㅎㄱ', '도감', 'ㄷㄱ', 'ehrkagyrhk', 'ergr', 'ehrka', 'er'],
                        description="도감의 효과를 확인합니다.",
                        usage="[박제 개수]",
                        pass_context=True)
    @app_commands.describe(collected="박제한 아이템의 개수 (0 ~ 135)")
    async def collection_power(self, ctx: commands.Context, collected: commands.Range[int, 0, 135]):
        """일반 도감에 박제된 아이템의 개수에 따라 결정되는 도감 효과를 확인하는 명령어입니다. `[박제 개수]`는 0 또는 1 ~ 135의 자연수여야 하며 필수로 입력해야 합니다.
        도감 효과는 공식을 유추하여 계산하기 때문에 실제 파머모 효과와 약간의 오차가 있을 수 있습니다. 공식은 다음과 같습니다.
        > <:exp:1037828199679266899> **쓰다듬기 경험치(배)**: 1+(n/60) (소수점은 버림)
        > ⚕️ **아픈 작물 치료 확률(%)**: max((n-60)\*(1/12), 0)
        > 🧫 **효모 획득 확률(%)**: 10+(n/6)
        > 💚 **잃은 체력 비례 회복(%)**: 7+(n\*0.03)
        > 😁 **성장 속도 증가(%)**: 120+(n/12)
        *\* Special thanks to 네티#4444*"""
        embed = collection_power_embed(collected)
        await ctx.reply(embed=embed)

    @collection_power.error
    async def collection_power_error(self, ctx, error):
        if isinstance(error, commands.RangeError):
            collected = error.value
            if len(str(collected)) > 30: # 주어진 수가 30자리수가 넘는 경우
                await ctx.reply("멈춰!")
            else:
                embed = collection_power_embed(collected)
                await ctx.reply(embed=embed)



    # @calculator.command(name="개간비용",
    #                     aliases=['ㄱㄱㅂㅇ', '개간', 'ㄱㄱ', 'rorksqldyd', 'rrqd', 'rorks', 'rr'],
    #                     description="밭을 개간하는데 필요한 딸기 수를 확인합니다.",
    #                     usage="[밭 순번]",
    #                     pass_context=True)
    # @app_commands.describe(cultivate="개간하는 밭의 순번 (1 ~ 20)")
    # async def cultivate(self, ctx: commands.Context, cultivate: commands.Range[int, 1, 20]):
    #     """."""
    #     embed = collection_power_embed(cultivate)
    #     await ctx.reply(embed=embed)
    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if isinstance(error, commands.RangeError):
    #         await ctx.reply("0에서 135 사이의 정수로 입력해주세요.")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Calculator(bot))