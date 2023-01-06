import discord
from discord import app_commands, Interaction, Object
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord.app_commands import Choice
from modules.database import *
from modules.get import *
from modules.utils import *



def search_embed(best: dict, guild_id: int = 0, user_id: int = 0):
    if best['type'] == "item" and best['id'] == "gem":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"<:blue_haired_moremi:1037828198261600337>의 재화. 이걸로 작물을 거래하거나 상점에서 아이템을 구매하는 등의 용도로 다양하게 사용할 수 있다.", color=discord.Color(0x5dadec))
        try:
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, data = get_user_info(user_id)
            embed.add_field(name="보유 수량", value=f"`{data['gem']}`", inline=True)
        except:
            pass
        embed.set_footer(text="[재화] 보석")
        return embed


    elif best['type'] == "item" and best['id'] == "strawberry":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"<:blue_haired_moremi:1037828198261600337>의 재화. 이걸로 밭을 개간하거나 시설물을 증축하는 등의 용도로 다양하게 사용할 수 있다.", color=discord.Color(0xbe1931))
        try:
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, data = get_user_info(user_id)
            embed.add_field(name="보유 수량", value=f"`{data['strawberry']}`", inline=True)
        except:
            pass
        embed.set_footer(text="[재화] 딸기")
        return embed


    elif best['type'] == "item":
        if best['craftables'] is None:
            color = discord.Color(0x202225)
        else:
            color = discord.Color(0x34495e)
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"{best['description_ko']}", color=color)
        try: # 개인 메시지이거나 로그인이 안된 유저인 사용하는 경우
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, weight, max_weight, inv_item_list = get_user_inventory(user_id)
            item_quantity = get_item_quantity_from_inventory(inv_item_list, best['id'])
            embed.add_field(name="보유 수량", value=f"`{item_quantity}`", inline=True)
            embed.add_field(name="개당 무게", value=f"`{best['weight']}`", inline=True)
            if best['weight']*item_quantity/max_weight != 0:
                embed.add_field(name="총 무게", value=f"`{best['weight']*item_quantity}` (`{best['weight']*item_quantity/max_weight*100:.2f}%`)", inline=True)
        except:
            embed.add_field(name="개당 무게", value=f"`{best['weight']}`", inline=True)

        if best['options'] is not None:
            option_list = [['health', '💙 활동력 회복', ''],
                        ['divisibleHealth', '💙 활동력 회복', ' (나눠쓰기 가능)'], 
                        ['healAcceleration', '💙 10분당 추가 활동력 회복량', '']]
            for i in option_list:
                if i[0] in best['options']:
                    value = best['options'][i[0]]
                    embed.add_field(name=i[1], value=f"`{value}`{i[2]}", inline=True)
            option_list = [['maxHealth', '최대 활동력'],
                           ['capacity', '⏲️ 광장 수용 가능 무게'],
                           ['pf', '물리 공격력'],
                           ['mf', '마법 공격력'],
                           ['pr', '물리 방어력'],
                           ['mr', '마법 공격력'],
                           ['speed', '기동력'],
                           ['concentration', '집중력'],
                           ['ferocity', '<:ferocity:1037828201533145088> 맹렬'],
                           ['mentality', '<:mentality:1037828204330750032> 신성'],
                           ['agility', '<:agility:1037828196592263208> 기민'],
                           ['tenacity', '<:tenacity:1037828205756829777> 완고'],
                           ['harmonicity', '<:harmonicity:1037828202594320496> 조화']]
            for i in option_list:
                if i[0] in best['options']:
                    value = best['options'][i[0]]
                    if type(value) is int:
                        embed.add_field(name=i[1], value=f"`{arrow_number(value)}`", inline=True)
                    elif type(value) is list:
                        embed.add_field(name=i[1], value=f"`{arrow_number(value[1])}` ~ `{arrow_number(value[2])}`", inline=True)
            if "lifespan" in best['options']:
                lifespan = best['options']['lifespan']
                embed.add_field(name="🧓 기대 수명", value=f"{convert_seconds_to_time_text(int(lifespan/1000))}", inline=True)
            if "expiredAt" in best['options']:
                expired_at = best['options']['expiredAt']
                embed.add_field(name="⌛ 만료일", value=f"<t:{int(expired_at/1000)}:D>", inline=True)
            if "buffByEating" in best['options']:
                buff_by_eating = best['options']['buffByEating']
                buff_id = list(buff_by_eating.keys())
                buff_duration = list(buff_by_eating.values())
                for i in range(len(buff_id)):
                    buff = fetch_buff_info(buff_id[i])
                    embed.add_field(name=f"먹어서 버프 발동: {buff['name_ko']}", value=f">>> {buff['icon']} {buff['description_ko']}\n⏰ 지속 시간: {convert_seconds_to_time_text(int(buff_duration[i]/1000))}", inline=False)
            if "coupon" in best['options']:
                coupon = best['options']['coupon']
                if coupon != "variable": # coupon이 동적이 아닌경우
                    coupon = list(coupon.items()) # [('5', {'match': [1, 3]}), ('10', {'pill': 1}), ('20', {'box-strawberry': 1}), ('300', {'medal-heart': 1})]
                    coupon_text = ""
                    for exchange in coupon:
                        exchange = list(exchange) # 튜플을 리스트로
                        exchange[1] = list(exchange[1].items())
                        for item in exchange[1]:
                            i = fetch_item_info(item[0])
                            if isinstance(item[1], int):
                                coupon_text += f"{exchange[0]}개 **➝** {i['icon']} **{i['name_ko']}** × {item[1]}개\n"
                            elif isinstance(item[1], list):
                                coupon_text += f"{exchange[0]}개 **➝** {i['icon']} **{i['name_ko']}** × {item[1][0]} ~ {item[1][1]}개\n"
                    embed.add_field(name="♻ 교환하기", value=coupon_text, inline=False)
                else: # 동적인 경우 (작물교환권)
                    embed.add_field(name="♻ 교환하기", value="10개 **➝** **작물** × 1개", inline=False)
        if best['craftables'] is not None:
            text = f"<:exp:1037828199679266899> 레벨 {best['level']}부터 만들 수 있어요.\n"
            for i in range(len(best['craftables'])):
                facility = fetch_facility_info(best['craftables'][i]['place'])
                if best['craftables'][i]['amount'][0] != best['craftables'][i]['amount'][1]:
                    text += f"{facility['icon']} **{facility['name_ko']}**에서 만점일 때 {best['craftables'][i]['amount'][0]} ~ {best['craftables'][i]['amount'][1]}개 만들어져요.\n"
                else:
                    text += f"{facility['icon']} **{facility['name_ko']}**에서 만점일 때 {best['craftables'][i]['amount'][0]}개 만들어져요.\n"
            if type(best['ingredients']) is dict: # dict 형식인 경우 - {'soy-paste': 3, 'tofu': 1, 'potato': 1, 'msg': 1}
                best['ingredients'] = list(best['ingredients'].items()) # [('soy-paste', 3), ('tofu', 1), ('potato', 1), ('msg', 1)]
            for i in range(len(best['ingredients'])):
                item = fetch_item_info(best['ingredients'][i][0])
                text += f"> {item['icon']} **{item['name_ko']}** × {best['ingredients'][i][1]}개\n"
            embed.add_field(name="제작 방법", value=text, inline=False)

        footer_text = f"[아이템] {item_category_to_text(best['category'])}"
        footer_text += " | 옮기기 불가" if best['vested']      == 1 else " | 옮기기 가능"
        footer_text += " | 버리기 불가" if best['planted']     == 1 else ""
        footer_text += " | 사용 아이템" if best['usable']      == 1 else ""
        footer_text += " | 도감 아이템" if best['collectible'] == 1 else " | 박제 불가"
        embed.set_footer(text=footer_text)
        return embed


    elif best['type'] == "crop":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"{best['description_ko']}", color=discord.Color(0x57f288))
        embed.add_field(name="작물 심기", value=f"<:exp:1037828199679266899> 레벨 {best['level']}부터 심을 수 있어요.\n🍓 딸기가 {best['strawberry']}개 필요해요.", inline=False)
        embed.add_field(name="성장 속도",   value=f"{crop_characteristic_to_text(best['growth'])}", inline=True)
        embed.add_field(name="필요 수분",   value=f"{crop_characteristic_to_text(best['water'])}",  inline=True)
        embed.add_field(name="필요 비옥도", value=f"{crop_characteristic_to_text(best['soil'])}",   inline=True)
        embed.add_field(name="병충해 내성", value=f"{crop_characteristic_to_text(best['health'])}", inline=True)

        footer_text = "[작물] "
        if best['is_tree'] == 1: footer_text += "나무"
        else: footer_text += "일반"
        embed.set_footer(text=footer_text)
        return embed


    elif best['type'] == "facility":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"{best['description_ko']}", color=discord.Color(0xa84300))
        embed.add_field(name="시설물 짓기", value=f"<:exp:1037828199679266899> 레벨 {best['level']}부터 지을 수 있어요.", inline=False)

        for i in range(len(best['build_costs'])):
            field_name = ""
            for j in range(i+1): field_name += "⭐"
            field_name += " 단계"

            build_costs = best['build_costs'][i]
            build_costs = list(build_costs.items())
            field_value = f"**착수 비용**\n> 🍓 **딸기** × {best['level']*(i+1)*(i+1)}개\n"
            for j in range(len(build_costs)):
                item = fetch_item_info(build_costs[j][0])
                field_value += f"> {item['icon']} **{item['name_ko']}**  × {build_costs[j][1]}개\n"

            options = best['options'][i]
            field_value += "**기능**\n>>> "
            if "dimension" in options:  
                field_value += f"⚒ **경작지 크기**\n└ `{options['dimension'][0]}x{options['dimension'][1]}칸`\n"
            if "maxWeight" in options:
                field_value += f"⏲ **인벤토리 최대 무게**\n└ `+{options['maxWeight']}`\n"
            if "maxLuggage" in options:
                field_value += f"⏲ **광장 인벤토리 최대 무게**\n└ `+{options['maxLuggage']}`\n"
            if "healAcceleration" in options:
                field_value += f"💙 **10분당 활동력 회복량**\n└ `+{options['healAcceleration']}`\n"
            if "dispensingInterval" in options:
                field_value += f"🚿 **분무 주기**\n└ `{options['dispensingInterval']}시간마다 한 번`\n"
            if "maxFloor" in options:
                field_value += f"🪜 **최심 층수**\n└ `지하 {options['maxFloor']}층`\n"
            if "maxLevel" in options:
                field_value += f"📈 **레벨 제한**\n└ `{options['maxLevel']}레벨 아이템까지 제작 가능`\n"
            if "wildAnimalAvoidance" in options:
                field_value += f"⛓ **야생동물 방어율**\n└ `+{int(options['wildAnimalAvoidance']*100)}%p`\n"
            if "taskLength" in options:
                field_value += f"📏 **작업 대기열 길이**\n└ `{options['taskLength']}`\n"
            if "maxDistance" in options:
                field_value += f"🚏 **순간이동 최대 거리**\n└ `{options['maxDistance']}칸`\n"
            if "craftBonus" in options:
                field_value += f"✨ **제작 효율 증가**\n└ `+{int(options['craftBonus']*100)}%p`\n" if options['craftBonus'] != 0 else ""
            if "taskBonus" in options:
                field_value += f"✨ **작업 효율 증가**\n└ `+{int(options['taskBonus']*100)}%p`\n" if options['taskBonus'] != 0 else ""
            if options == {}: # 빈 dict인 경우 (기능이 없는 경우)
                field_value += "**없음**"
            embed.add_field(name=field_name, value=field_value, inline=True)

        footer_text = "[시설물] "
        if type(best['size']) is list:
            footer_text += f"일반 시설물 | {best['size'][0]}x{best['size'][1]}"
            if best['rotatable'] == 1:
                footer_text += f" 또는 {best['size'][1]}x{best['size'][0]}"
            footer_text += " 크기"
        else:
            footer_text += f"광장 시설물"
        embed.set_footer(text=footer_text)
        return embed


    elif best['type'] == "buff":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"{best['description_ko']}", color=discord.Color(0x5dadec))
        field_value = ""
        items = fetch_item_info_all()
        for item in items:
            try:
                field_value += f"> {item['icon']} **{item['name_ko']}** | {convert_seconds_to_time_text(item['options']['buffByEating'][best['id']]/1000)}\n"
            except:
                pass
        embed.add_field(name="이 버프를 가지고 있는 음식", value=field_value, inline=False)

        embed.set_footer(text=f"[버프]")
        return embed


    elif best['type'] == "stat":
        embed=discord.Embed(title=f"{best['icon']} {best['name_ko']}", description=f"{best['description_ko']}", color=discord.Color(0xe67e22))
        field_value = ""
        items = fetch_item_info_all()
        if best['id'] != "expiredAt":
            for item in items:
                if item['options'] is not None: # item에 옵션이 있고
                    if best['id'] in item['options']: # best['id']에 검색하려는 옵션이 있는 경우
                        field_value += f"> {item['icon']} **{item['name_ko']}** | {item_category_to_text(item['category'], True)} | "
                        value = item['options'][best['id']]
                        if type(value) is int:
                            field_value += f"`{arrow_number(item['options'][best['id']])}`"
                        elif type(value) is list:
                            field_value += f"`{arrow_number(value[1])}` ~ `{arrow_number(value[2])}`"
                        field_value += "\n"
            if field_value != "":
                embed.add_field(name="이 능력치를 가지고 있는 장비", value=field_value, inline=False)
            else:
                embed.add_field(name="이 능력치를 가지고 있는 장비", value="없음", inline=False)
        else: # 기간제 아이템만
            for item in items:
                if item['options'] is not None:
                    if "expiredAt" in item['options']:
                        field_value += f"> {item['icon']} **{item['name_ko']}** | <t:{int(item['options'][best['id']] /1000)}:D>에 만료\n"
            embed.add_field(name="기간제 아이템", value=field_value, inline=False)

        embed.set_footer(text=f"[능력치]")
        return embed



class SearchButton(Button):
    def __init__(self, best:dict, guild_id:int, author_id:int):
        if best['id'] == "gem" and best['type'] == "item":
            button_style = discord.ButtonStyle.blurple
        elif best['id'] == "strawberry" and best['type'] == "item":
            button_style = discord.ButtonStyle.red
        elif best['type'] == "item":
            button_style = discord.ButtonStyle.gray
        elif best['type'] == "crop":
            button_style = discord.ButtonStyle.green
        elif best['type'] == "facility":
            button_style = discord.ButtonStyle.red
        elif best['type'] == "buff":
            button_style = discord.ButtonStyle.blurple
        elif best['type'] == "stat":
            button_style = discord.ButtonStyle.red
        super().__init__(label=best['name_ko'], emoji=best['icon'], style=button_style)
        self.best      = best
        self.guild_id  = guild_id
        self.author_id = author_id
    async def callback(self, interaction: discord.Interaction):
        embed = search_embed(self.best, self.guild_id, interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)



class SearchView(View):
    children: SearchButton
    def __init__(self, result_count:int, result_list:list, guild_id:int, author_id:int):
        super().__init__()
        if result_count >= 2:
            for i in range(result_count):
                self.add_item(SearchButton(result_list[i], guild_id, author_id))



class Search(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="검색",
                             aliases=['search', '검', 'ㄱㅅ', 'ㄳ', 'ㄱ', 'rjator', 'rja', 'rt', 'r', 'item', '템', 'ㅇㅇㅌ', 'ㅌ', 'dkdlxpa', 'xpa', 'x'],
                             description="아이템, 작물, 시설물, 버프를 검색하여 관련 정보를 보여줍니다.",
                             with_app_command=True)
    @app_commands.describe(keyword="검색할 항목 (아이템/작물/시설물/버프/능력치 이름)")
    async def search(self, ctx: commands.Context, *, keyword: str):
        await ctx.defer(ephemeral = True)
        db_list = search_db(keyword)

        result = []
        result_count = 0
        for i in range(4):
            if db_list[i]['ratio'] == 1:
                result.append(db_list[i])
                result_count += 1
            else:
                break

        if result_count == 0: # embeds가 없을 때
            if db_list[0]['ratio'] >= 0.5 and db_list[0]['ratio'] >= db_list[1]['ratio']*1.02 or db_list[0]['ratio'] >= 0.25 and db_list[0]['ratio'] >= db_list[1]['ratio']*1.15: # ratio가 50% 이상이고 다음 ratio에 비해 2% 이상 높거나 / 25% 이상이고 다음 ratio에 비해 15% 이상 높은 경우
                if isinstance(ctx.channel, discord.channel.DMChannel):
                    embed = search_embed(db_list[0], 0, 0)
                else:
                    embed = search_embed(db_list[0], ctx.guild.id, ctx.author.id)
                await ctx.reply(embed=embed)

            else:
                description = ""
                suggest_count = 0
                for i in range(15):
                    if db_list[i]['ratio'] <= 0.15 or db_list[0]['ratio'] >= db_list[i]['ratio']*1.15: # ratio가 15% 이하거나 가장 높은 ratio에 비해 15% 이상 낮은 경우
                        break
                    description += f"{db_list[i]['icon']} **{db_list[i]['name_ko']}**\n"
                    suggest_count += 1
                if suggest_count != 0:
                    embed=discord.Embed(title="이것을 찾으셨나요?", description=description, color=discord.Color.random())
                    await ctx.reply(content="", embed=embed)
                else:
                    await ctx.reply(f"`{keyword}`에 해당하는 적절한 아이템/작물/시설물/버프/능력치를 찾을 수 없습니다.")

        elif result_count == 1:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                embed = search_embed(db_list[0], 0, 0)
            else:
                embed = search_embed(db_list[0], ctx.guild.id, ctx.author.id)
            await ctx.reply(embed=embed)

        else: # 결과가 여러개
            await ctx.reply(f"`{keyword}`에 해당하는 검색 결과가 여러 개입니다.\n아래 버튼을 눌러 원하는 결과를 확인하세요.", view=SearchView(result_count, result, ctx.guild.id, ctx.author.id))
    @search.autocomplete("keyword")
    async def search_autocomplete(self, interaction: Interaction, current: str,) -> Choice[str]:
        choice = ['벽돌', '모래', '성냥', '라면', '연구소', '대장간', '조리실', '양파', '크로뮴', '고구마', '효모', '군고구마', '호박']
        return [Choice(name=keyword, value=keyword) for keyword in choice if current.lower() in keyword.lower()]



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Search(bot))