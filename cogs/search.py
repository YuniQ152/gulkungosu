import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ui import Button, View
from discord.app_commands import Choice
from modules.database import *
from modules.get import *
from modules.utils import *



def search_embed(result: dict, guild_id: int = 0, user_id: int = 0) -> discord.Embed:

    def search_embed_gem(guild_id: int = 0, user_id: int = 0) -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"<:blue_haired_moremi:1037828198261600337>의 재화. 이걸로 작물을 거래하거나 상점에서 아이템을 구매하는 등의 용도로 다양하게 사용할 수 있다.", color=discord.Color(0x5dadec))
        try:
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, user_info = get_user_info(user_id)
            embed.add_field(name="보유 수량", value=f"`{user_info['gem']}`", inline=True)
        except:
            pass
        embed.set_footer(text="[재화] 보석")
        return embed


    def search_embed_strawberry(guild_id: int = 0, user_id: int = 0) -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"<:blue_haired_moremi:1037828198261600337>의 재화. 이걸로 밭을 개간하거나 시설물을 증축하는 등의 용도로 다양하게 사용할 수 있다.", color=discord.Color(0xbe1931))
        try:
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, user_info = get_user_info(user_id)
            embed.add_field(name="보유 수량", value=f"`{user_info['strawberry']}`", inline=True)
        except:
            pass
        embed.set_footer(text="[재화] 딸기")
        return embed


    def search_embed_item(guild_id: int = 0, user_id: int = 0) -> discord.Embed:
        if result['craftables'] is None:
            color = discord.Color(0x202225)
        else:
            color = discord.Color(0x34495e)
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=color)

        try:
            response_code, user_id = get_user_id(guild_id, user_id)
            response_code, weight, max_weight, inv_item_list = get_user_inventory(user_id)
            response_code, user_info = get_user_info(user_id)
            item_quantity = get_item_quantity_from_inventory(inv_item_list, result['id'])
            gem = int(user_info['gem'])
            embed.add_field(name="보유 수량", value=f"`{item_quantity}`", inline=True)
            embed.add_field(name="개당 무게", value=f"`{result['weight']}`", inline=True)
            if result['weight']*item_quantity/max_weight != 0:
                embed.add_field(name="총 무게", value=f"`{result['weight']*item_quantity}` (`{result['weight']*item_quantity/max_weight*100:.2f}%`)", inline=True)
        except: # 개인 메시지이거나 로그인이 안된 유저인 경우
            embed.add_field(name="개당 무게", value=f"`{result['weight']}`", inline=True)

        if result['options'] is not None:
            if "expiredAt" in result['options']:
                expired_at = result['options']['expiredAt']
                embed.add_field(name="⌛ 기간제 아이템", value=f"<t:{int(expired_at/1000)}:D>", inline=True)

            option_list = [['health', '💙 활동력 회복', ''],
                           ['divisibleHealth', '💙 활동력 회복', ' (나눠쓰기 가능)']]
            for key, name, suffix in option_list:
                if key in result['options']:
                    value = result['options'][key]
                    embed.add_field(name=name, value=f"`{value}`{suffix}", inline=True)

            if "healAcceleration" in result['options']:
                value = result['options']['healAcceleration']
                embed.add_field(name="💙 활동력 회복량 변화", value=f"`{int(value*100)}%p`", inline=True)

            if "rainResistance" in result['options']:
                value = result['options']['rainResistance']
                embed.add_field(name="🌧️ 비 저항력", value=f"`{int(value*100)}%p`", inline=True)
                
            option_list = [['maxHealth', '최대 활동력'],
                           ['capacity', '⏲️ 광장 수용 가능 무게'],
                           ['pf', '물리 공격력'],
                           ['mf', '마법 공격력'],
                           ['pr', '물리 방어력'],
                           ['mr', '마법 방어력'],
                           ['speed', '기동력'],
                           ['concentration', '집중력'],
                           ['ferocity', '<:ferocity:1037828201533145088> 맹렬'],
                           ['mentality', '<:mentality:1037828204330750032> 신성'],
                           ['agility', '<:agility:1037828196592263208> 기민'],
                           ['tenacity', '<:tenacity:1037828205756829777> 완고'],
                           ['harmonicity', '<:harmonicity:1037828202594320496> 조화']]
            for key, name in option_list:
                if key in result['options']:
                    value = result['options'][key]
                    if type(value) is int:
                        embed.add_field(name=name, value=f"`{arrow_number(value)}`", inline=True)
                    elif type(value) is list:
                        embed.add_field(name=name, value=f"`{arrow_number(value[1])}` ~ `{arrow_number(value[2])}`", inline=True)

            if "lifespan" in result['options']:
                lifespan = result['options']['lifespan']
                embed.add_field(name="🧓 기대 수명", value=f"{convert_seconds_to_time_text(int(lifespan/1000))}", inline=True)

            if "buffByEating" in result['options']:
                buff_by_eating = result['options']['buffByEating']
                buff_id = list(buff_by_eating.keys())
                buff_duration = list(buff_by_eating.values())
                for i in range(len(buff_id)):
                    buff = fetch_buff_one(buff_id[i])
                    embed.add_field(name=f"먹어서 버프 발동: {buff['name']}", value=f">>> {buff['icon']} {buff['description']}\n⏰ 지속 시간: {convert_seconds_to_time_text(int(buff_duration[i]/1000))}", inline=False)

            if "buffByUsing" in result['options']:
                buff_by_using = result['options']['buffByUsing']
                buff_id = list(buff_by_using.keys())
                buff_duration = list(buff_by_using.values())
                for i in range(len(buff_id)):
                    buff = fetch_buff_one(buff_id[i])
                    embed.add_field(name=f"써서 버프 발동: {buff['name']}", value=f">>> {buff['icon']} {buff['description']}\n⏰ 지속 시간: {convert_seconds_to_time_text(int(buff_duration[i]/1000))}", inline=False)

            if "coupon" in result['options']:
                coupon = result['options']['coupon']
                if coupon != "variable": # coupon이 동적이 아닌경우
                    coupon = list(coupon.items()) # [('5', {'match': [1, 3]}), ('10', {'pill': 1}), ('20', {'box-strawberry': 1}), ('300', {'medal-heart': 1})]
                    coupon_text = ""
                    for exchange in coupon:
                        for item in list(exchange[1].items()):
                            i = fetch_item_one(item[0])
                            coupon_text += f"{exchange[0]}개 **➝** {i['icon']} **{i['name']}** × {tilde_number(item[1])}개\n"
                    embed.add_field(name="♻ 교환하기", value=coupon_text, inline=False)
                else: # 동적인 경우 (작물교환권)
                    embed.add_field(name="♻ 교환하기", value="10개 **➝** **작물** × 1개", inline=False)
                    
        if result['craftables'] is not None:
            text = f"<:exp:1037828199679266899> 레벨 {result['level']}부터 만들 수 있어요.\n"
            for i in range(len(result['craftables'])):
                craftable = result['craftables'][i]
                facility = fetch_facility_one(craftable['place'])
                if craftable['amount'][0] == craftable['amount'][1] and craftable['amount'][0] == 1:
                    text += f"{facility['icon']} **{facility['name']}**에서 1개 만들어져요."
                else:
                    text += f"{facility['icon']} **{facility['name']}**에서 만점을 기준으로 {tilde_number(craftable['amount'])}개 만들어져요."
                
                if craftable['coproducts'] is not None: # craftable['coproducts'] == {'soy-paste': [3, 4]}
                    coproducts = list(craftable['coproducts'].items())
                    text += " 이 때 부산물로 "
                    for coproduct in coproducts:
                        item = fetch_item_one(coproduct[0])
                        text += f"{item['icon']} **{item['name']}** {tilde_number(coproduct[1])}개, "
                    text = text[:-2]
                    text += "를 얻어요.\n"
                else:
                    text += "\n"
            if type(result['ingredients']) is dict: # dict 형식인 경우 - {'soy-paste': 3, 'tofu': 1, 'potato': 1, 'msg': 1}
                result['ingredients'] = list(result['ingredients'].items()) # [('soy-paste', 3), ('tofu', 1), ('potato', 1), ('msg', 1)]
            for i in range(len(result['ingredients'])):
                item = fetch_item_one(result['ingredients'][i][0])
                try:
                    if item['id'] == "gem":
                        item_quantity = gem
                    else:
                        item_quantity = get_item_quantity_from_inventory(inv_item_list, item['id'])
                    if item_quantity >= result['ingredients'][i][1]:
                        text += f"> {item['icon']} **{item['name']}** × {result['ingredients'][i][1]}개 `({item_quantity}/{result['ingredients'][i][1]})`\n"
                    else:
                        text += f"> {item['icon']} **{item['name']}** × {result['ingredients'][i][1]}개 `({item_quantity}/{result['ingredients'][i][1]})❌`\n"
                except:
                    text += f"> {item['icon']} **{item['name']}** × {result['ingredients'][i][1]}개\n"
            text += step_text(result['steps'])
            embed.add_field(name="제작 방법", value=text, inline=False)

        footer_text = f"[아이템] {item_category_to_text(result['category'])}"
        footer_text += " | 옮기기 불가" if result['vested']      == 1 else " | 옮기기 가능"
        footer_text += " | 버리기 불가" if result['planted']     == 1 else ""
        footer_text += " | 사용 아이템" if result['usable']      == 1 else ""
        footer_text += " | 도감 아이템" if result['collectible'] == 1 else " | 박제 불가"
        if result['options'] is not None:
            if "maxQuantity" in result['options']:
                footer_text += f" | {result['options']['maxQuantity']}개까지 보유 가능"
        embed.set_footer(text=footer_text)
        return embed


    def search_embed_crop() -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=discord.Color(0x57f288))
        embed.add_field(name="작물 심기", value=f"<:exp:1037828199679266899> 레벨 {result['level']}부터 심을 수 있어요.\n🍓 딸기가 {result['strawberry']}개 필요해요.", inline=False)
        embed.add_field(name="😁 성장 속도",   value=f"{crop_characteristic_to_text(result['growth'])}", inline=True)
        embed.add_field(name="💧 필요 수분",   value=f"{crop_characteristic_to_text(result['water'])}",  inline=True)
        embed.add_field(name="🍔 필요 비옥도", value=f"{crop_characteristic_to_text(result['soil'])}",   inline=True)
        embed.add_field(name="🦠 병충해 내성", value=f"{crop_characteristic_to_text(result['health'])}", inline=True)

        footer_text = "[작물] "
        if result['is_tree'] == 1: footer_text += "나무"
        else: footer_text += "일반"
        embed.set_footer(text=footer_text)
        return embed


    def search_embed_facility() -> discord.Embed:
    
        def facility_option_text(name: str, value: str) -> str:
            text = f"**{name}**\n```diff\n{value}```"
            return text
    
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=discord.Color(0xa84300))
        embed.add_field(name="시설물 짓기", value=f"<:exp:1037828199679266899> 레벨 {result['level']}부터 지을 수 있어요.", inline=False)

        for i in range(len(result['build_costs'])):
            field_name = f"{'⭐' * (i+1)} 단계"

            build_costs = result['build_costs'][i]
            build_costs = list(build_costs.items())
            field_value = f"**착수 비용**\n> 🍓 **딸기** × {result['level']*(i+1)*(i+1)}개\n"
            for coproduct in range(len(build_costs)):
                item = fetch_item_one(build_costs[coproduct][0])
                field_value += f"> {item['icon']} **{item['name']}**  × {build_costs[coproduct][1]}개\n"

            options = result['options'][i]
            field_value += "**기능**\n>>> "
            if "dimension" in options:
                field_value += facility_option_text(name="⚒ 경작지 크기",
                                                    value=f"{options['dimension'][0]}x{options['dimension'][1]}칸")
            if "maxLevel" in options:
                field_value += facility_option_text(name="📈 레벨 제한",
                                                    value=f"{options['maxLevel']}레벨 아이템까지 제작 가능")
            if "pantryLevel" in options:
                field_value += facility_option_text(name="📈 레벨 제한",
                                                    value=f"{options['pantryLevel']}레벨 아이템까지 등록 가능")
            if "maxWeight" in options:
                field_value += facility_option_text(name="⏲ 인벤토리 최대 무게",
                                                    value=f"+{format(options['maxWeight'], ',')}")
            if "maxLuggage" in options:
                field_value += facility_option_text(name="⏲ 광장 인벤토리 최대 무게",
                                                    value=f"+{format(options['maxLuggage'], ',')}")
            if "pantryCapacity" in options:
                field_value += facility_option_text(name="⏲ 자판기 인벤토리 최대 무게",
                                                    value=f"{format(options['pantryCapacity'], ',')}")
            if "healAcceleration" in options:
                field_value += facility_option_text(name="💙 활동력 회복량 변화",
                                                    value=f"+{int(options['healAcceleration']*100)}%p")
            if "dispensingInterval" in options:
                field_value += facility_option_text(name="🚿 분무 주기",
                                                    value=f"{options['dispensingInterval']}시간마다 한 번")
            if "maxFloor" in options:
                field_value += facility_option_text(name="🪜 최심 층수",
                                                    value=f"지하 {options['maxFloor']}층")
            if "wildAnimalAvoidance" in options:
                field_value += facility_option_text(name="⛓ 야생동물 방어율",
                                                    value=f"+{int(options['wildAnimalAvoidance']*100)}%p")
            if "taskLength" in options:
                field_value += facility_option_text(name="🔀 작업 대기열 길이",
                                                    value=f"{options['taskLength']}")
            if "maxDistance" in options:
                field_value += facility_option_text(name="🚏 순간이동 최대 거리",
                                                    value=f"{options['maxDistance']}칸")
            if "craftBonus" in options:
                if options['craftBonus'] != 0:
                    field_value += facility_option_text(name="✨ 제작 효율 증가",
                                                        value=f"+{int(options['craftBonus']*100)}%p")
            if "taskBonus" in options:
                if options['taskBonus'] != 0:
                    field_value += facility_option_text(name="✨ 작업 빠르기 증가",
                                                        value=f"+{int(options['taskBonus']*100)}%p")
            if options == {}: # 빈 dict인 경우 (기능이 없는 경우)
                field_value += "**없음**"
            embed.add_field(name=field_name, value=field_value, inline=True)

        footer_text = "[시설물] "
        if type(result['size']) is list:
            footer_text += f"일반 시설물 | {result['size'][0]}x{result['size'][1]}"
            if result['rotatable'] == 1:
                footer_text += f" 또는 {result['size'][1]}x{result['size'][0]}"
            footer_text += " 크기"
        else:
            footer_text += f"광장 시설물"
        embed.set_footer(text=footer_text)
        return embed


    def search_embed_buff() -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=discord.Color(0x5dadec))
        items = fetch_item_all()

        field_value = ""
        for item in items:
            try:
                field_value += f"> {item['icon']} **{item['name']}** | {convert_seconds_to_time_text(item['options']['buffByEating'][result['id']]/1000)}\n"
            except:
                pass
        if field_value != "":
            embed.add_field(name="이 버프를 먹어서 발동시킬 수 있는 음식", value=field_value, inline=False)

        field_value = ""
        for item in items:
            try:
                field_value += f"> {item['icon']} **{item['name']}** | {convert_seconds_to_time_text(item['options']['buffByUsing'][result['id']]/1000)}\n"
            except:
                pass
        if field_value != "":
            embed.add_field(name="이 버프를 써서 발동시킬 수 있는 아이템", value=field_value, inline=False)

        embed.set_footer(text=f"[버프]")
        return embed


    def search_embed_option() -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=discord.Color(0xe67e22))
        items = fetch_item_all()
        field_value = ""
        if result['id'] != "expiredAt":
            for item in items:
                if item['options'] is not None: # item에 옵션이 있고
                    if result['id'] in item['options']: # best['id']에 검색하려는 옵션이 있는 경우
                        field_value += f"> {item['icon']} **{item['name']}** | {item_category_to_text(item['category'], True)} | "
                        value = item['options'][result['id']]
                        if type(value) is int:
                            field_value += f"`{arrow_number(value)}`"
                        elif type(value) is float:
                            field_value += f"`{int(value*100)}%`"
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
                        field_value += f"> {item['icon']} **{item['name']}** | <t:{int(item['options'][result['id']] /1000)}:D>에 만료\n"
            embed.add_field(name="기간제 아이템", value=field_value, inline=False)

        embed.set_footer(text=f"[능력치]")
        return embed


    def search_embed_step() -> discord.Embed:
        embed=discord.Embed(title=f"{result['icon']} {result['name']}", description=f"{result['description']}", color=discord.Color.yellow())
        items = fetch_item_all()
        field_value = ""
        for item in items:
            if item['steps'] is not None:
                if item['steps'].count(result['id']) == 0:
                    pass
                elif item['steps'].count(result['id']) == 1:
                    field_value += f"> {item['icon']} **{item['name']}**\n"
                else:
                    field_value += f"> {item['icon']} **{item['name']}** × {item['steps'].count(result['id'])}\n"

        embed.add_field(name="이 제작 과정을 포함하는 아이템", value=field_value, inline=False)
        embed.set_footer(text=f"[제작 과정]")
        return embed

    
    if result['type'] == "item" and result['id'] == "gem":
        return search_embed_gem(guild_id, user_id)
    elif result['type'] == "item" and result['id'] == "strawberry":
        return search_embed_strawberry(guild_id, user_id)
    elif result['type'] == "item":
        return search_embed_item(guild_id, user_id)
    elif result['type'] == "crop":
        return search_embed_crop()
    elif result['type'] == "facility":
        return search_embed_facility()
    elif result['type'] == "buff":
        return search_embed_buff()
    elif result['type'] == "option":
        return search_embed_option()
    elif result['type'] == "step":
        return search_embed_step()
    


def embed_suggest(keyword: str, db_list: list) -> discord.Embed:
    description = ""
    suggest_count = 0
    for i in range(20):
        if db_list[i]['ratio'] <= 0.05 or db_list[0]['ratio'] >= db_list[i]['ratio']*1.5: # ratio가 5% 이하거나 가장 높은 ratio에 비해 50% 이상 낮은 경우 멈춤
            break
        description += f"{db_list[i]['icon']} **{db_list[i]['name']}**\n"
        suggest_count += 1

    if suggest_count != 0:
        embed=discord.Embed(title="이것을 찾으셨나요?", description=description, color=discord.Color.light_grey())
        return embed
    else:
        embed=discord.Embed(title="검색 결과 없음", description=f"`{keyword}`에 해당하는 적절한 아이템/작물/시설물/버프/능력치/제작 과정을 찾을 수 없습니다.", color=discord.Color.dark_grey())
        return embed



class SearchButton(Button):
    def __init__(self, best: dict, guild_id: int, author_id: int):
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
        elif best['type'] == "option":
            button_style = discord.ButtonStyle.red
        elif best['type'] == "step":
            button_style = discord.ButtonStyle.red
        super().__init__(label=best['name'], emoji=best['icon'], style=button_style)
        self.best      = best
        self.guild_id  = guild_id
        self.author_id = author_id
    async def callback(self, interaction: Interaction):
        embed = search_embed(self.best, self.guild_id, interaction.user.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)



class SearchView(View):
    children: SearchButton
    def __init__(self, result_count: int, result_list: list, guild_id: int, author_id: int):
        super().__init__()
        if result_count >= 2:
            for i in range(result_count):
                self.add_item(SearchButton(result_list[i], guild_id, author_id))



class Search(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="검색",
                             aliases=['search', '검', 'ㄱㅅ', 'ㄳ', 'ㄱ', 'rjator', 'rja', 'rt', 'r', 'item', '템', 'ㅇㅇㅌ', 'ㅌ', 'dkdlxpa', 'xpa', 'x'],
                             description="아이템, 작물, 시설물, 버프, 능력치, 제작 과정을 검색하여 관련 정보를 확인합니다.",
                             usage="[검색어]")
    @app_commands.describe(keyword="검색할 항목 (아이템/작물/시설물/버프/능력치/제작 과정 이름)")
    async def search(self, ctx: commands.Context, *, keyword: str):
        """아이템, 작물, 시설물, 버프, 능력치, 제작 과정를 검색하여 관련 정보를 확인하는 명령어입니다. `[검색어]`는 검색할 아이템, 작물, 시설물, 버프, 능력치, 제작 과정의 이름이여야 하며 필수로 입력해야 합니다.
        검색어와 가장 유사한 파머모에 존재하는 항목을 나타내며 검색 결과에 따라 하나의 결과가 나올 수도, 여러 개의 결과가 나올 수도, 아니면 검색 결과가 나타나는 대신 추천 검색어가 나타날 수도 있습니다. 검색은 아이템의 한국어 이름, 영어 이름, 또는 아이템 ID로 검색할 수 있으며, 한국어 이름의 경우 초성으로도 검색이 가능합니다.
        __아이템__의 경우 어두운 회색(제작 방법이 없는 경우) 또는 코발트 블루색(제작 방법이 있는 경우)으로 나타나며, 명령어를 사용한 여행자의 아이템 보유 개수, 개당 무게, 아이템 제작 방법 등의 정보가 나타납니다.
        __작물__의 경우 춘록색으로 나타나며, 작물을 심는 데 필요한 딸기, 성장 속도, 필요 수분/비옥도 등의 정보가 나타납니다.
        __시설물__의 경우 갈색으로 나타나며, 시설물의 착수 비용과 기능 등의 정보가 나타납니다.
        __버프__의 경우 하늘색으로 나타나며, 먹거나 사용했을 때 해당 버프가 발동하는 아이템 목록과, 아이템별 버프 지속시간이 나타납니다.
        __능력치__의 경우 주황색으로 나타나며, 해당 능력치를 변동시키는 아이템 목록과, 아이템별 능력치 변동 수치가 나타납니다.
        __제작 과정__의 경우 노란색으로 나타나며, 아이템을 만드는 데 해당 제작 과정이 들어가 있는 아이템 목록이 나타납니다.
        """
        
        db_list = search_db(keyword)

        result = []
        result_count = 0
        for i in range(4):
            if db_list[i]['ratio'] >= 0.97:
                result.append(db_list[i])
                result_count += 1
            else:
                break

        if result_count == 0: # embeds가 없을 때
            if (db_list[0]['ratio'] >= 0.5 and db_list[0]['ratio'] > db_list[1]['ratio']*1.02) or (db_list[0]['ratio'] >= 0.25 and db_list[0]['ratio'] >= db_list[1]['ratio']*1.15): # ratio가 50% 이상이고 다음 ratio에 비해 2% 이상 높거나 / 25% 이상이고 다음 ratio에 비해 15% 이상 높은 경우
                if db_list[0]['name'] == db_list[1]['name'] or (db_list[0]['aliases'] == db_list[1]['aliases'] and db_list[0]['aliases'] is not None): # 같은 이름의 아이템 + 작물
                    if db_list[0]['ratio'] >= 0.25 and db_list[0]['ratio'] >= db_list[2]['ratio']*1.15: # 다중 결과
                        if isinstance(ctx.channel, discord.channel.DMChannel):
                            embeds = [search_embed(db_list[0], 0, 0), search_embed(db_list[1], 0, 0)]
                        else:
                            embeds = [search_embed(db_list[0], ctx.guild.id, ctx.author.id), search_embed(db_list[1], ctx.guild.id, ctx.author.id)]
                        await ctx.reply(embeds=embeds)
                    else: # 검색 제안
                        embed = embed_suggest(keyword, db_list)
                        await ctx.reply(embed=embed)
                else: # 단일 결과
                    if isinstance(ctx.channel, discord.channel.DMChannel):
                        embed = search_embed(db_list[0], 0, 0)
                    else:
                        embed = search_embed(db_list[0], ctx.guild.id, ctx.author.id)
                    await ctx.reply(embed=embed)

            else: # 검색 제안
                embed = embed_suggest(keyword, db_list)
                await ctx.reply(embed=embed)

        elif result_count == 1:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                embed = search_embed(db_list[0], 0, 0)
            else:
                embed = search_embed(db_list[0], ctx.guild.id, ctx.author.id)
            await ctx.reply(embed=embed)

        elif result_count == 2 and (db_list[0]['name'] == db_list[1]['name'] or (db_list[0]['aliases'] == db_list[1]['aliases'] and db_list[0]['aliases'] is not None)): # 같은 이름의 아이템 + 작물
            if isinstance(ctx.channel, discord.channel.DMChannel):
                embeds = [search_embed(db_list[0], 0, 0), search_embed(db_list[1], 0, 0)]
            else:
                embeds = [search_embed(db_list[0], ctx.guild.id, ctx.author.id), search_embed(db_list[1], ctx.guild.id, ctx.author.id)]
            await ctx.reply(embeds=embeds)

        else: # 결과가 여러개
            if isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.reply(f"`{keyword}`에 해당하는 검색 결과가 여러 개입니다.\n아래 버튼을 눌러 원하는 결과를 확인하세요.", view=SearchView(result_count, result, 0, ctx.author.id))
            else:
                await ctx.reply(f"`{keyword}`에 해당하는 검색 결과가 여러 개입니다.\n아래 버튼을 눌러 원하는 결과를 확인하세요.", view=SearchView(result_count, result, ctx.guild.id, ctx.author.id))
    @search.autocomplete("keyword")
    async def search_autocomplete(self, interaction: Interaction, current: str) -> Choice[str]:
        db_list = search_db(current)
        choice = [d['name'] for d in db_list][:25]
        return [Choice(name=keyword, value=keyword) for keyword in choice if current.lower() in keyword.lower()]



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Search(bot))
