import discord
from discord.ext import commands
from modules.database import *
from modules.get import *
from modules.utils import *



class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.hybrid_command(name="도움",
                             aliases=['help', 'ㄷㅇ', '?', 'ehdna', 'ed'],
                             description="사용 가능한 명령어 목록을 보여줍니다.",
                             with_app_command=True)
    async def help(self, ctx: commands.Context):
        await ctx.defer(ephemeral = True)

        if isinstance(ctx.channel, discord.channel.DMChannel):
            embed_title = "📙 안녕하세요, 글쿤 고수입니다!"
        else:
            embed_title = "📙 안녕하세요, 여기서 다시 뵙네요!"
        embed=discord.Embed(title=embed_title, description=f"글쿤 고수 도움말 페이지에 오신 것을 환영합니다.\n이곳에 나열된 모든 명령어는 명령어 앞에 `.`을 붙여 채팅으로 입력하거나, 슬래시 커맨드(빗금 명령어)로 사용할 수 있습니다.\n명령어를 채팅으로 입력하는 경우, 초성으로도 사용할 수 있습니다.", color=discord.Color.yellow())

        with open("commands.json", "rt", encoding="UTF-8") as file:
            data = json.load(file)

        field_value=""
        for command in data:
            field_value += f"**{', '.join(command['displayName'])}**\n"
            field_value += f"{command['description']}\n"
            field_value += f"> 사용법: `{command['displayName'][0]}"
            for parameter in command['parameters']:
                if parameter['isOptional']: field_value += f" ({parameter['displayName']})"
                else:                       field_value += f" [{parameter['displayName']}]"
            field_value += f"`\n"
            if isinstance(ctx.channel, discord.channel.DMChannel) and command['allowDM'] is False:
                field_value += f"> (개인 메시지에서 사용 불가)\n"
            field_value += f"\n"
        embed.add_field(name="🤖 명령어 목록", value=field_value, inline=False)
        
        embed.add_field(name="💁 도움이 필요하시나요?", value=f"글쿤 고수의 질문, 건의, 버그 제보, 그 외의 다양한 것들을 받고 있어요.\n이러한 것들이 필요하시다면 [고등어 서버](https://discord.gg/WXjQZ3eJs5)의 포스트에 남겨주세요.", inline=False)
        bot_owner = await self.bot.fetch_user(self.bot.owner_id)
        embed.set_footer(text=f"Made by {bot_owner.name}#{bot_owner.discriminator}", icon_url=bot_owner.avatar.url)

        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.reply(content="", embed=embed)
        else:
            try:
                await ctx.author.send(content="", embed=embed)
                await ctx.reply(content="개인 메시지로 도움말을 보냈어요!")
            except:
                await ctx.reply(content="개인 메시지를 보낼려고 했는데, 보낼 수가 없어요! 개인 메시지 수신을 허용하고 저를 거부하지 말아주세요.")
            


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))