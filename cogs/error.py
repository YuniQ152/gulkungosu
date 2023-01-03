import discord
from discord.ext import commands
from datetime import datetime
import sys, traceback



class Error(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        # await self.bot.process_commands(message)
        if message.content.startswith("."):
            if isinstance(message.channel, discord.DMChannel): # DM
                text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {'D M':^50} | {'User: ' + message.author.name + message.author.discriminator:^24} | {message.content}"
                print(text)
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {'Server: ' + message.guild.name:^24} | {'Channel: #' + message.channel.name:^24} | {'User: ' + message.author.name + message.author.discriminator:^24} | {message.content}")

                embed = discord.Embed(title="명령어 사용됨", description="", color=discord.Color.blurple())
                embed.add_field(name="정보", value=f">>> **서　버:** {message.guild.name}\n**채　널:** {message.channel.mention} (#{message.channel.name})\n**사용자:** {message.author.name}#{message.author.discriminator}", inline=False)
                embed.add_field(name="내용", value=message.content, inline=False)
                embed.timestamp = datetime.now()
                message_channel = self.bot.get_channel(1050124516652752921)
                await message_channel.send(embed=embed)



    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"필요한 아규먼트가 없습니다.\n올바른 사용법: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f"아규먼트 형식이 잘못되었습니다.\n올바른 사용법: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f":stopwatch: 명령어가 재사용 대기 중입니다.\n**{error.retry_after:.2f}**초 후에 다시 시도해주세요.", ephemeral = True)
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
        elif isinstance(error, discord.HTTPException):
            await ctx.reply(f"메시지를 보낼려고 했는데 너무 길어요!", ephemeral = True)
        else:
            print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

            embed = discord.Embed(title="오류 발생", description=f"예기치 못한 오류가 발생했습니다.\n문제가 계속된다면 고등어 서버에 버그 제보를 남겨주세요.```{ctx.command} 명령어를 처리하는 도중 문제가 발생했습니다.```", timestamp=ctx.message.created_at, color=discord.Color.red())
            await ctx.reply(embed=embed)

            embed = discord.Embed(title="오류 발생", description=f"```Ignoring exception in command {ctx.command}\n{error}```", timestamp=ctx.message.created_at, color=discord.Color.red())
            message_channel = self.bot.get_channel(1050124516652752921)
            await message_channel.send(content="<@776986070708518913>", embed=embed)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Error(bot))