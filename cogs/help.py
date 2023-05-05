import discord
from discord import app_commands
from discord.ext import commands
from discord.errors import Forbidden

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title="📒 안녕하세요, 글쿤 고수입니다!",
                              description=f"**__글쿤 고수__**는 **<:blue_haired_moremi:1037828198261600337>파란 머리 모레미**의 서드파티 봇이에요.\n"
                                           "이곳에 나열된 모든 명령어는 명령어 앞에 `.`을 붙여 채팅으로 입력하거나, 슬래시 커맨드(빗금 명령어)로 사용할 수 있어요.\n"
                                           "명령어를 채팅으로 사용하는 경우에는 초성으로도 사용할 수 있어요.",
                              color=discord.Color(0xffcc4d))
        command_list = []
        for cog, commands in mapping.items():
            for command in commands:
                if not command.hidden:
                    command_list.append(f"> `{command.name.ljust(5, '　')}` {command.description}")

        command_list = sorted(command_list)
        embed.add_field(name="🤖 명령어 목록", value='\n'.join(command_list), inline=False)
        embed.add_field(name="💁 도움이 필요하신가요?",
                        value="글쿤 고수의 질문, 건의, 버그 제보, 그 외의 다양한 것들을 언제나 환영합니다!\n"
                              "이러한 것들이 필요하시다면 [고등어 서버](https://discord.gg/WXjQZ3eJs5)의 포스트에 남겨주세요.",
                        inline=False)
        bot_owner = await ctx.bot.fetch_user(ctx.bot.owner_id)
        embed.set_footer(text=f"Made by {bot_owner.name}#{bot_owner.discriminator}", icon_url=bot_owner.avatar.url)
        await ctx.reply(embed=embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        channel = self.get_destination()
        await channel.send("pass") # 특정 Cog의 명령어 도움말 출력

    async def send_group_help(self, group):
        ctx = self.context
        embed = discord.Embed(title=f"📗 명령어 그룹: {group.name}", description=group.help, color=discord.Color(0x77b255))
        commands = sorted(group.commands, key=lambda c: c.name)
        command_list = []
        for command in commands:
            if not command.hidden:
                command_list.append(f"> `{command.name.ljust(5, '　')}` {command.description}")
        if command_list:
            embed.add_field(name="🤖 하위 명령어 목록", value="\n".join(command_list), inline=False)
        if group.aliases:
            embed.add_field(name="텍스트 커맨드 동의어", value=", ".join(group.aliases), inline=False)
        bot_owner = await ctx.bot.fetch_user(ctx.bot.owner_id)
        embed.set_footer(text=f"Made by {bot_owner.name}#{bot_owner.discriminator}", icon_url=bot_owner.avatar.url)
        await ctx.reply(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(title=f"📘 명령어: {command.name}", color=discord.Color(0x55acee))
        usage = ""
        if command.parent:
            usage += f"{command.full_parent_name} "
        usage += f"{command.name}"
        if command.usage:
            usage += f" {command.usage}"

        embed.add_field(name="사용법", value=f"`{usage}`", inline=False)
        detail = command.help or command.description
        checks = [f.__qualname__.split('.')[0] for f in command.checks]
        if 'guild_only' in checks:
            detail += "\n*(이 명령어는 개인 메시지에서 사용할 수 없습니다.)*"
        embed.add_field(name="세부 정보", value=detail, inline=False)
        if command.aliases:
            embed.add_field(name="텍스트 커맨드 동의어", value=", ".join(command.aliases), inline=False)

        bot_owner = await ctx.bot.fetch_user(ctx.bot.owner_id)
        embed.set_footer(text=f"Made by {bot_owner.name}#{bot_owner.discriminator}", icon_url=bot_owner.avatar.url)
        await ctx.reply(embed=embed)

    # async def send_error_message(self, error):
    #     """If there is an error, send a embed containing the error."""
    #     channel = self.get_destination() # this defaults to the command context channel
    #     await channel.send(error)


async def on_help_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(str(error))
    else:
        raise error


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        self.bot.remove_command("help")

    @commands.hybrid_command(name="도움",
                             aliases=['help', 'ㄷㅇ', '?', 'ehdna', 'ed'],
                             description="명령어 목록과 명령어의 설명을 확인합니다.",
                             usage="(명령어)")
    @app_commands.describe(command="명령어 이름")
    async def help(self, ctx: commands.Context, *, command: str = None):
        """글쿤 고수의 명령어 목록과 명령어에 대한 자세한 설명을 확인하는 명령어입니다. `(명령어)`에는 확인하려는 명령어의 이름이 들어가고, 입력하지 않을 경우 전체 명령어 목록을 나타냅니다.
        전체 명령어 목록은 노란색(📒)으로, 명령어 그룹은 초록색(📗)으로, 개별 명령어는 파란색(📘)으로 나타납니다."""
        if command:
            c = self.bot.get_command(command)
            if c:
                await ctx.send_help(c)
            else:
                await ctx.reply(f"`{command}`(이)라는 명령어는 존재하지 않습니다.")
        else:
            await ctx.send_help()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))