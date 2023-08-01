import discord
from discord.ext import commands
from datetime import datetime



class Log(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("."):
            # if message.author.id != 776986070708518913:
                if isinstance(message.channel, discord.DMChannel): # DM
                    text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} || DM || {message.author.name + '#' + message.author.discriminator} || {message.content}"
                    print(text)
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} || {message.guild.name} || {message.channel.name} || {message.author.name + '#' + message.author.discriminator} || {message.content}")

                    embed = discord.Embed(title="명령어 사용됨", description="", color=discord.Color.blurple())
                    embed.add_field(name="정보", value=f">>> **서버:** {message.guild.name}\n**채널:** {message.channel.mention} (#{message.channel.name})\n**유저:** {message.author.name}#{message.author.discriminator}", inline=False)
                    embed.add_field(name="내용", value=message.content, inline=False)
                    embed.timestamp = datetime.now()
                    message_channel = self.bot.get_channel(1050124516652752921)
                    await message_channel.send(embed=embed)



    #     if len(message.embeds) != 0 and (message.author.id == 870304475326332968 or message.author.id == 1055865319467520140):
    #         embed = message.embeds[0]
    #         if "님의 갱" in embed.title or "'s Pit" in embed.title:
    #             print(embed.title)
    #             # await message.channel.send("갱감지")



    # @commands.Cog.listener()
    # async def on_message_edit(self, message_before, message_after):
    #     if len(message_after.embeds) != 0 and (message_after.author.id == 870304475326332968 or message_after.author.id == 1055865319467520140):
    #         embed = message_after.embeds[0]
    #         if "님의 갱" in embed.title or "'s Pit" in embed.title:
    #             description = embed.description.split("\n")
    #             health      = int(embed.fields[0].value)        # 현재 활동력
    #             consumption = int(embed.fields[1].value)        # 1회 채굴 시 소모 활동력
    #             reward      = embed.fields[2].value.split("\n") # 채굴 보상
    #             print(description)
    #             print(reward)
    #             # await message.channel.send("갱감지")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Log(bot))
