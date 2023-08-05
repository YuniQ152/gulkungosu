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
            activity = discord.Activity(type = discord.ActivityType.playing, name = "글쿤 고수 v2.0 개발 중"),
            intents = intents
        )

        self.initial_extensions = ["cogs.help",
                                   "cogs.cofarm",
                                   "cogs.farm",
                                   "cogs.health",
                                   "cogs.inventory",
                                   "cogs.stats",
                                   "cogs.agora",
                                   "cogs.land",
                                   "cogs.search",
                                   "cogs.graph",
                                   "cogs.calculator",
                                   "cogs.translator",
                                   "cogs.log",
                                   "cogs.error"]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await self.tree.sync()
        check.start()

    async def on_ready(self):
        print(f"logged in as {bot.user} (ID: {bot.user.id})")
        print(f"Discord.py Version: {discord.__version__}")
        print("----------------")


bot = Bot()

@tasks.loop(seconds=600) # 10분
async def check():
    await bot.wait_until_ready()
    message_channel = bot.get_channel(1025073541743386624) # 메시지를 보낼 채널 (개인 채널 ID)

    cofarm_id_list = [809843576094588960, 844551435986665473, 844551361932820550]
    user_id = 1234
    total_spendable = 0

    embeds = []
    for cofarm_id in cofarm_id_list:
        response_code, farms, contributions = get_cofarm_info(809809541385682964, cofarm_id)
        if response_code != 200: await message_channel.send(api_error_message(response_code), ephemeral=True); return

        plowable  = 0    # 밭 갈기 가능 수
        waterable = 0    # 물 주기 가능 수
        severe_count = 0 # 위독한 작물 수
        severe_text = "" # 위독한 작물 텍스트
        score = 0        # 공동농장 점수
        for crop in farms:

            if crop is not None: # 작물이 심어져 있을 때
                crop_id      = crop['staticCropId'] # 작물ID
                status       = crop['status']       # 상태: 0 정상 | 1 다갈증 | 2 나쁜 곰팡이 | 3 지렁이
                health       = crop['health']       # 체력
                humidity     = crop['humidity']     # 수분
                fertility    = crop['fertility']    # 비옥도
                acceleration = crop['acceleration'] # 성장 가속
                growth       = crop['growth']       # "dirt" "germination" "maturity" "fruitage"

                score += (health                               **(3-health)   *0.75 +
                            (fertility if fertility <= 0.9 else 1)**(3-fertility)*0.2  +
                            (humidity  if humidity  <= 0.9 else 1)**(3-humidity )*0.05
                            ) / len(farms)

                if fertility <= 0.9:
                    plowable += 1
                if humidity <= 0.9:
                    waterable += 1

                if humidity <= 0.2 or fertility <= 0.3 or health <= 0.5:
                    severe_count += 1
                    severe_text += generate_crop_text(crop)

        crop_count = 0
        for crop in farms:
            if crop is not None: # 작물이 심어져 있는 경우
                crop_count += 1

        activitible_text=""
        activitible_text += f"> 🚿 **물 뿌리기**: `{waterable}`\n"
        activitible_text += f"> ⚒️ **밭 갈기**: `{plowable}`"

        embed_title = f"{cofarm_id} 공동농장\n"
        description = f">>> 🔗 바로가기: <#{cofarm_id}>\n"
        description += f"🌱 작물 수: `{crop_count}`/{len(farms)}"
        if crop_count == len(farms): description += "\n"
        else:                        description += " `❗` \n"
        if str(user_id) in contributions:
            if contributions[str(user_id)] != 0 and contributions[str(user_id)] != 1:
                description += f"🏆 기여도: `{int(contributions[str(user_id)]*100)}%`\n"
        description += f"💯 농장 점수: {int(score*100)}점"
        color = embed_color(score)
        embed=discord.Embed(title=embed_title, description=description, color=discord.Color.from_rgb(color[0], color[1], color[2]))
        if plowable != 0 or waterable != 0:
            embed.add_field(name=f"💙 활동력 소비 가능: {waterable*5+plowable*20}", value=activitible_text, inline=False)
        if severe_count != 0:
            embed.add_field(name=f"😵 위독함: {severe_count}곳", value=severe_text, inline=False)

        embeds.append(embed)
        total_spendable += waterable*5+plowable*20
    

    
    response_code, user_info = get_user_info(1234)
    if response_code != 200: await message_channel.send(api_error_message(response_code)); return
    user_health = user_info['health'] # 현재 활동력

    if total_spendable < 100:
        await message_channel.send(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 현재 활동력: 💙 {user_health}", embeds=embeds)
    else:
        await message_channel.send(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 현재 활동력: 💙 {user_health} <@776986070708518913>", embeds=embeds)


bot.run(TOKEN, reconnect=True)