import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from modules.database import *
from modules.get import *
from modules.utils import *



def stats_embed(user, user_info, target = None, target_info = None):
    if target is None: # 타겟이 없는 경우
        embed=discord.Embed(title=f"{user.display_name}님의 능력치", description="", color=discord.Color(0xe67e22))
        embed.add_field(name="물리 공격력", value=user_info['stats']['pf'])
        embed.add_field(name="마법 공격력", value=user_info['stats']['mf'])
        embed.add_field(name="기동력",      value=user_info['stats']['speed'])
        embed.add_field(name="물리 방어력", value=user_info['stats']['pr'])
        embed.add_field(name="마법 방어력", value=user_info['stats']['mr'])
        embed.add_field(name="집중력",      value=user_info['stats']['concentration'])
        return embed
    else: # 타겟이 있는 경우
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
            

        embed=discord.Embed(title=f"{user.display_name} vs {target.display_name} 능력치 비교", description="", color=discord.Color(0xe67e22))
        embed.add_field(name=user.display_name, value=embed_user_field_value)
        embed.add_field(name="vs", value=compare_field_value)
        embed.add_field(name=target.display_name, value=embed_target_field_value)
        return embed


def agora_embed(member: discord.Member, inv_list: list) -> discord.Embed:
    ticket_list = []

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

    embed=discord.Embed(
        title=f"{member.display_name}님의 광장 입장권",
        description=f"> 🔗 사용하기: </agora:910495388300091392>\n> 🎟️ 입장권 개수: {len(ticket_list)}",
        color=discord.Color(0xbe1931)
    )
    embed.add_field(name="만료일", value=text)

    return embed



class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.tree.add_command(app_commands.ContextMenu(name="능력치", callback=self.stats_contextmenu))


    @commands.hybrid_command(name="능력치",
                             aliases=['stats', '능력', 'ㄴㄹㅊ', 'ㄴㄹ', 'smdfurcl', 'smdfur', 'sfc', 'sf'],
                             description="현재 능력치를 보여줍니다.",
                             usage="(사용자) (비교 대상)")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(member="능력치 정보를 조회할 대상. 입력하지 않을 경우 본인이 조회됨.", target="능력치 정보를 비교할 대상.")
    async def stats(self, ctx: commands.Context, member: discord.Member = None, *, target: discord.Member = None):
        """능력치 정보를 확인하는 명령어입니다. `(사용자)`는 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 자기 자신을 선택한 것으로 간주합니다. `(비교 대상)`은 Discord 서버에 있는 사용자로, 멤버 ID, 멤버 멘션, 사용자명#태그, 사용자명 또는 서버 내 별명이여야 하며 입력하지 않을 경우 비교 대상은 없습니다.
        `(비교 대상)`이 없을 때: `(사용자)`의 능력치를 보여줍니다.
        `(비교 대상)`이 있을 때: `(사용자)`와 `(비교 대상)`의 능력치를 보여주고 각 능력치별로 어느 쪽의 능력치가 얼마나 높은지 보여줍니다.
        *(능력치에는 물리 공격력, 물리 방어력, 마법 공격력, 마법 방어력, 기동력, 집중력이 있습니다.)*"""
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
        response_code, id = get_user_id(interaction.guild.id, interaction.user.id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return
        response_code, user_info = get_user_info(id)
        if response_code != 200: await interaction.response.send_message(api_error_message(response_code, interaction.user), ephemeral=True); return

        if interaction.user != target: # 자기 자신의 능력치를 조회하지 않는 경우 (타겟이 있는 경우)
            response_code, id = get_user_id(interaction.guild.id, target.id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return
            response_code, target_info = get_user_info(id)
            if response_code != 200: await interaction.response.send_message(api_error_message(response_code, target), ephemeral=True); return

            embed = stats_embed(interaction.user, user_info, target, target_info)
        else: # 자기자신 (타겟이 없는 경우)
            embed = stats_embed(interaction.user, user_info)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stats(bot))
    