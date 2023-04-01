import discord
from discord.ext import commands
import sys, traceback



class Error(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command is None:
            usage = ""
        elif ctx.command.parent is None:
            usage = f"{ctx.prefix}{ctx.command.name} {ctx.command.usage}"
        else:
            usage = f"{ctx.prefix}{ctx.command.full_parent_name} {ctx.command.name} {ctx.command.usage}"

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"필요한 인자가 없습니다.\n올바른 사용법: `{usage}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f"인자 형식이 잘못되었습니다.\n올바른 사용법: `{usage}`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f":stopwatch: 명령어가 재사용 대기 중입니다.\n**{error.retry_after:.1f}**초 후에 다시 시도해주세요.", ephemeral = True)
        elif isinstance(error, commands.CommandNotFound):
            pass
            # await ctx.reply(f"이런 명령어는 없습니다.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"이 명령어를 실행할 권한이 없습니다.", ephemeral = True)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.reply(f"이 명령어는 현재 비활성화되었습니다.", ephemeral = True)
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.reply("이 명령어는 개인 메시지에서 작동하지 않아요.")
            except discord.HTTPException:
                pass
        else:
            error_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            print(f"Ignoring exception in command {ctx.command}:\n{error_str}", file=sys.stderr)

            embed = discord.Embed(title="오류 발생", description=f"예기치 못한 오류가 발생했습니다.\n문제가 계속된다면 [고등어 서버](https://discord.gg/WXjQZ3eJs5)에 버그 제보를 남겨주세요.```{ctx.command} 명령어를 처리하는 도중 문제가 발생했습니다.```", timestamp=ctx.message.created_at, color=discord.Color.red())
            await ctx.reply(embed=embed)
            
            embed = discord.Embed(title="오류 발생", description=f"```Ignoring exception in command {ctx.command}\n{error}\n\n{error_str}```", timestamp=ctx.message.created_at, color=discord.Color.red())
            embed.add_field(name="정보", value=f">>> **서버:** {ctx.guild.name}\n**채널:** {ctx.channel.mention} (#{ctx.channel.name})\n**유저:** {ctx.author.name}#{ctx.author.discriminator}", inline=False)
            embed.add_field(name="내용", value=ctx.message.content, inline=False)
            message_channel = self.bot.get_channel(1050124516652752921)
            await message_channel.send(content="<@776986070708518913>", embed=embed)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Error(bot))