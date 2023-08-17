import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *


def agora_embed(member: discord.Member, inv_list: list) -> discord.Embed:
    ticket_list = []
    ticket_count = 0

    for item in inv_list:
        if item['staticId'] == "ticket-agora":
            ticket = item
            if "expiredAt" in ticket:
                ticket['expiredAt'] = int(ticket['expiredAt'] / 1000)
            else:
                ticket['expiredAt'] = 999999999999
            ticket_list.append(ticket)

    text = ""
    ticket_list = sorted(ticket_list, key=lambda x: x['expiredAt'])
    for ticket in ticket_list:
        if ticket['expiredAt'] != 999999999999:
            text += f"<t:{ticket['expiredAt']}:f> (<t:{ticket['expiredAt']}:R>) × {ticket['quantity']}개\n"
        else:
            text += f"무기한 × {ticket['quantity']}개"
        ticket_count += ticket['quantity']

    embed=discord.Embed(
        title=f"{member.display_name}님의 광장 입장권",
        description=f"> 🔗 사용하기: </agora:910495388300091392>\n> 🎟️ 입장권 개수: {ticket_count}",
        color=discord.Color(0xbe1931)
    )
    embed.add_field(name="만료일", value=text)

    return embed


class Agora(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # self.bot.tree.add_command(app_commands.ContextMenu(name="광장 입장권", callback=self.agora_contextmenu))



    @commands.hybrid_command(name="광장입장권",
                             aliases=['agora_ticket', 'agoraticket', 'ㄱㅈㅇㅈㄱ', '광장', 'ㄱㅈ', '입장권', 'ㅇㅈㄱ', 'rwdwr', 'rhkdwkd', 'rw', 'dlqwkdrnjs', 'dwr'],
                             description="광장 입장권의 개수와 만료일 확인합니다.",
                             usage="(사용자)")
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Agora(bot))
    