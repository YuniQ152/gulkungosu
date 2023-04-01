import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.app_commands import Choice
from modules.database import *
from modules.get import *
from modules.utils import *



class Stock(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot




    @commands.hybrid_command(name="그래프",
                             aliases=['graph', '그랲', '그래', 'ㄱㄿ', 'ㄱㄹㅍ', 'ㄱㄹ', 'rmfovm', 'rmfov', 'rmfo', 'rfv', 'rf'],
                             description="작물의 시세를 그래프로 확인합니다.",
                             usage="[작물]")
    @app_commands.describe(crop="작물 이름")
    async def graph(self, ctx: commands.Context, *, crop: str):
        """최근 1주일간 거래된 작물의 시세를 그래프로 확인하는 명령어입니다. `[작물]`은 작물의 이름이여야 하며 필수로 입력해야 합니다."""
        full_item_list = fetch_item_info_all()
        crop_list = add_ratio_in_dict(crop, full_item_list, "crop", ['송진', '인터갤럭틱 가스'])

        if crop_list[0]['ratio'] >= 0.5 or crop_list[0]['ratio'] >= crop_list[1]['ratio']*1.4: # 가장 높은 ratio가 50% 이상일 경우 -또는- 가장 높은 ratio가 두 번째로 높은 ratio보다 40% 이상 높을 경우
            best = crop_list[0]
            response_code, trade_history = get_crop_trade_history(best['id'])
            if response_code == 404: await ctx.reply(f"{best['icon']} **{best['name_ko']}**는 최근 1주일간 거래된 기록이 없습니다."); return
            elif response_code != 200: await ctx.reply(api_error_message(response_code), ephemeral=True); return

            price = []
            date = []
            for i in trade_history:
                price.insert(0, int(i['totalGem']) / i['quantity'])
                date.insert(0, convert_datetime(i['date']/1000))
            generate_graph(date, price)
            await ctx.reply(f"{best['icon']} **{best['name_ko']}**의 최근 1주일 시세 그래프입니다.", file=discord.File("trade.png"))
        elif crop_list[0]['ratio'] <= 0.45: # 가장 높은 ratio가 45% 이하일 경우
            await ctx.reply(f"`{crop}`에 해당하는 적절한 작물을 찾을 수 없습니다.")
        else:
            description = ""
            for i in range(len(crop_list)):
                if crop_list[i]['ratio'] == 0 or crop_list[0]['ratio'] >= crop_list[i]['ratio']*1.4: # ratio가 0이거나 가장 높은 ratio에 비해 40% 이상 낮은 경우
                    break
                description += f"{crop_list[i]['icon']} **{crop_list[i]['name_ko']}**\n"
            embed=discord.Embed(title="이것을 찾으셨나요?", description=description, color=discord.Color.random())
            await ctx.reply(content="", embed=embed)
    @graph.autocomplete("crop")
    async def graph_autocomplete(self, interaction: Interaction, current: str,) -> Choice[str]:
        choice = ['감자', '고구마', '마늘', '밀', '벼', '사탕수수', '솜', '애호박', '양파', '옥수수', '콩', '토마토', '호박']
        return [Choice(name=crop, value=crop) for crop in choice if current.lower() in crop.lower()]



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stock(bot))