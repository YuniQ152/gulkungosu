import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



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
        description += f"{items[i]['icon']} **{items[i]['name']}** × {items[i]['quantity']}개 (무게 {items[i]['total_weight']}) `{items[i]['total_weight']/inv_max_weight*100:.1f}%`\n"
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


class Inventory(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="인벤토리", callback=self.inventory_contextmenu))


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



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Inventory(bot))
    