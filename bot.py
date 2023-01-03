import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from datetime import datetime
from modules.database import *
from modules.get import *
from modules.utils import *

load_dotenv()
TOKEN=os.getenv("DISCORD_BOT_TOKEN")

def get_prefix(bot, message):
    prefixes = ["."]
    return commands.when_mentioned_or(*prefixes)(bot, message)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix = get_prefix,
            case_insensitive = True,
            sync_command = True,
            owner_id = 776986070708518913,
            activity = discord.Activity(type = discord.ActivityType.playing, name = "✨v1.2.2 업데이트 완료! - 농장 명령어가 개편되었습니다"),
            intents = intents)

        self.initial_extensions = ["cogs.general",
                                   "cogs.server",
                                   "cogs.user",
                                   "cogs.search",
                                   "cogs.stock",
                                   "cogs.log",
                                   "cogs.error"]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await self.tree.sync()
        # await self.tree.sync(guild = Object(id = 785849670092980225))
        check_loop.start()
                              
    async def on_ready(self):
        print(f"logged in as {bot.user} (ID: {bot.user.id})")
        print(f"Discord.py Version: {discord.__version__}")
        print("------------")


bot = Bot()
bot.remove_command("help")

@tasks.loop(seconds=600) # 10분
async def check_loop():
    await bot.wait_until_ready()
    message_channel = bot.get_channel(1025073541743386624) # 메시지를 보낼 채널 (개인 채널 ID)

    response_code, user_info = get_user_info(1234)
    if response_code != 200: await message_channel.send(api_error_message(response_code), ephemeral=True); return
    user_health = user_info['health'] # 현재 활동력
    if user_health >= 85:
        await message_channel.send(content=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 현재 활동력: 💙 {user_health} <@776986070708518913>")
    else:
        await message_channel.send(content=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 현재 활동력: 💙 {user_health}")


bot.run(TOKEN, reconnect=True)