import os, requests, json, sqlite3, time
from dotenv import load_dotenv

load_dotenv()

step = 0
def print_step(text: str, linebreak: bool = True) -> str:
    if linebreak is True:
        print(f"[STEP {step}] {text}")
    else:
        print(f"[STEP {step}] {text}", end="")

def get_item_info(item_name: str) -> tuple:
    try:
        url = "https://farm.jjo.kr/api/static/item/" + str(item_name)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    except:
        print("재시도")
        url = "https://farm.jjo.kr/api/static/item/" + str(item_name)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    content = json.loads(response.content)
    id = content["data"]["id"]
    icon = content["data"]["icon"]
    category = content["data"]["category"]
    level = content["data"]["level"]
    weight = content["data"]["weight"]
    options = None if content["data"]["options"] is None else str(content["data"]["options"])
    vested = 1 if content["data"]["vested"] == True else 0
    planted = 1 if content["data"]["planted"] == True else 0
    usable = 1 if content["data"]["usable"] == True else 0
    collectible = 1 if content["data"]["collectible"] == True else 0
    name_ko = content["names"]["ko"]
    name_en = content["names"]["en"]
    description_ko = content["descriptions"]["ko"].replace("<:blue_haired_moremi:923442506195173456>", "<:blue_haired_moremi:1037828198261600337>")
    description_en = content["descriptions"]["en"].replace("<:blue_haired_moremi:923442506195173456>", "<:blue_haired_moremi:1037828198261600337>")
    return id, icon, category, level, weight, options, vested, planted, usable, collectible, name_ko, name_en, description_ko, description_en

def get_item_recipe(item_id):
    url = "https://farm.jjo.kr/api/static/recipe/" + str(item_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        content = json.loads(response.content)
        craftables = content["craftables"]
        ingredients = content["ingredients"]
        steps = content["steps"]
        return(response.status_code, craftables, ingredients, steps)
    elif response.status_code == 406:
        return(response.status_code, None, None, None)

def get_facility_info(facility_id):
    url = "https://farm.jjo.kr/api/static/facility/" + str(facility_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    content = json.loads(response.content)
    id_ = content['data']['id']
    icon = content['data']['icon']
    color = content['data']['color']
    level = content['data']['level']
    size = str(content["data"]["size"]) if "size" in content["data"] else None
    build_costs = str(content["data"]["buildCosts"]) if content["data"]["buildCosts"] is not None else None
    options = str(content["data"]["options"]) if content["data"]["options"] is not None else None
    rotatable = int(content['data']['rotatable'])
    name_ko = content["names"]["ko"]
    name_en = content["names"]["en"]
    description_ko = content["descriptions"]["ko"]
    description_en = content["descriptions"]["en"]
    return id_, icon, color, level, size, build_costs, options, rotatable, name_ko, name_en, description_ko, description_en

def get_crop_info(crop_id):
    url = "https://farm.jjo.kr/api/static/crop/" + str(crop_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    content = json.loads(response.content)
    id_ = content['data']['id']
    icon = content['data']['icon']
    level = content['data']['level']
    strawberry = content["data"]['strawberry']
    is_tree = 1 if content["data"]["isTree"] == True else 0
    growth = content["data"]['characteristics']['growth']
    water = content["data"]['characteristics']['water']
    soil = content["data"]['characteristics']['soil']
    health = content["data"]['characteristics']['health']
    name_ko = content["names"]["ko"]
    name_en = content["names"]["en"]
    description_ko = content["descriptions"]["ko"]
    description_en = content["descriptions"]["en"]
    return id_, icon, level, strawberry, is_tree, growth, water, soil, health, name_ko, name_en, description_ko, description_en

RUN_STEP = [0, 1, 2, 3, 4, 5, 6]

with open("getdata.json", "rt", encoding="UTF-8") as file:
    data = json.load(file)
items        = data['item']
crops        = data['crop']
facilities   = data['facility']
achievements = data['achievement']
buffs        = data['buff']
options      = data['option']

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()
conn.execute("CREATE TABLE IF NOT EXISTS item(id TEXT PRIMARY KEY, icon TEXT, category TEXT, level INTEGER, weight INTEGER, options TEXT, vested INTEGER, planted INTEGER, usable INTEGER, collectible INTEGER, name_ko TEXT, name_en TEXT, description_ko TEXT, description_en TEXT, craftables TEXT, ingredients TEXT, steps TEXT, aliases TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS crop(id TEXT PRIMARY KEY, icon TEXT, level INTEGER, strawberry INTEGER, is_tree INTEGER, growth TEXT, water TEXT, soil TEXT, health TEXT, name_ko TEXT, name_en TEXT, description_ko TEXT, description_en TEXT, aliases TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS facility(id TEXT PRIMARY KEY, icon TEXT, color TEXT, level INTEGER, size TEXT, build_costs TEXT, options TEXT, rotatable INTEGER, name_ko TEXT, name_en TEXT, description_ko TEXT, description_en TEXT, aliases TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS buff(id TEXT PRIMARY KEY, icon TEXT, options TEXT, name_ko TEXT, name_en TEXT, description_ko TEXT, description_en TEXT, aliases TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS stat(id TEXT PRIMARY KEY, icon TEXT, name_ko TEXT, name_en TEXT, description_ko TEXT, description_en TEXT, aliases TEXT)")
# conn.execute("CREATE TABLE IF NOT EXISTS pit(user INTEGER PRIMARY KEY, guild TEXT, reward TEXT, time INTEGER)")
# conn.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, guild_id INTEGER, user_id INTEGER, guild_name TEXT, user_name_bhmo TEXT, user_name_discord TEXT)")
# conn.execute("CREATE TABLE IF NOT EXISTS guild(id INTEGER PRIMARY KEY, name TEXT, cofarm_channel_id TEXT)")
conn.commit()

step = 1
# STEP_2: API 아이템 조회 및 DB 저장 (static-item)
def add_item():
    print_step(f"아이템 정보를 데이터베이스에 추가합니다.")
    for i in range(len(items)):
        if isinstance(items[i], str):
            item_info = get_item_info(items[i])
            cur.execute("INSERT OR REPLACE INTO item(id, icon, category, level, weight, options, vested, planted, usable, collectible, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (item_info))
        elif isinstance(items[i], list):
            item_info = list(get_item_info(items[i][0]))
            item_info.append(items[i][1])
            cur.execute("INSERT OR REPLACE INTO item(id, icon, category, level, weight, options, vested, planted, usable, collectible, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (item_info))
        else:
            raise TypeError
        item_id = item_info[0]
        response_code, craftables, ingredients, steps = get_item_recipe(item_id)
        if response_code == 200:
            cur.execute("UPDATE item SET craftables=?, ingredients=?, steps=? WHERE id=?", (str(craftables), str(ingredients), str(steps), item_id))
            print_step(f"[{item_info[1]} {item_info[10]}] 아이템 및 제작 방법 추가됨. ({i+1}/{len(items)})")
        elif response_code == 406:
            print_step(f"[{item_info[1]} {item_info[10]}] 아이템 추가됨. 제작 방법 없음. ({i+1}/{len(items)})")
        conn.commit()
        time.sleep(1)
    print_step(f"완료. 모든 아이템을 성공적으로 추가했습니다.\n")
if 1 in RUN_STEP:
    add_item()

step = 2
# STEP_2: 작물 DB 저장
def add_crop():
    print_step(f"앞으로 {len(crops)}개의 작물을 데이터베이스에 추가합니다.")
    for i in range(len(crops)):
        if isinstance(crops[i], str):
            crop_info = list(get_crop_info(crops[i]))
            cur.execute("INSERT OR REPLACE INTO crop(id, icon, level, strawberry, is_tree, growth, water, soil, health, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (crop_info))
        elif isinstance(crops[i], list):
            crop_info = get_crop_info(crops[i][0])
            crop_info.append(crops[i][1])
            cur.execute("INSERT OR REPLACE INTO crop(id, icon, level, strawberry, is_tree, growth, water, soil, health, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (crop_info))
        else:
            raise TypeError
        conn.commit()
        print_step(f"[{crop_info[1]} {crop_info[9]}] 작물 추가됨. ({i+1}/{len(crops)})")
        time.sleep(0.32)
    print_step(f"완료. 모든 작물을 성공적으로 추가했습니다.\n")
if 2 in RUN_STEP:
    add_crop()

step = 3
# STEP_3: 시설물 DB 저장
def add_facility():
    print_step(f"앞으로 {len(facilities)}개의 시설물을 데이터베이스에 추가합니다.")
    for i in range(len(facilities)):
        if isinstance(facilities[i], str):
            facility_info = get_facility_info(facilities[i])
            cur.execute("INSERT OR REPLACE INTO facility(id, icon, color, level, size, build_costs, options, rotatable, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (facility_info))
        elif isinstance(facilities[i], list):
            facility_info = list(get_facility_info(facilities[i][0]))
            facility_info.append(facilities[i][1])
            cur.execute("INSERT OR REPLACE INTO facility(id, icon, color, level, size, build_costs, options, rotatable, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (facility_info))
        conn.commit()
        print_step(f"[{facility_info[1]} {facility_info[8]}] 시설물 추가됨. ({i+1}/{len(facilities)})")
        time.sleep(0.32)
    print_step(f"완료. 모든 시설물을 성공적으로 추가했습니다.\n")
if 3 in RUN_STEP:
    add_facility()

step = 4
# STEP_4: 업적 DB 저장
def add_achievement():
    pass
if 4 in RUN_STEP:
    add_achievement()

step = 5
def add_buff():
    print_step(f"앞으로 {len(buffs)}개의 버프를 데이터베이스에 추가합니다.")
    for i in range(len(buffs)):
        buffs[i]['options'] = str(buffs[i]['options'])
        cur.execute("INSERT OR REPLACE INTO buff(id, icon, options, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?,?)", (list(buffs[i].values())))
        conn.commit()
        print_step(f"[{buffs[i]['icon']} {buffs[i]['name_ko']}] 버프 추가됨. ({i+1}/{len(buffs)})")
    print_step(f"완료. 모든 버프를 성공적으로 추가했습니다.\n")
if 5 in RUN_STEP:
    add_buff()

step = 6
def add_stat():
    print_step(f"앞으로 {len(options)}개의 능력치를 데이터베이스에 추가합니다.")
    for i in range(len(options)):
        cur.execute("INSERT OR REPLACE INTO stat(id, icon, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?)", (list(options[i].values())))
        conn.commit()
        print_step(f"[{options[i]['icon']} {options[i]['name_ko']}] 능력치 추가됨. ({i+1}/{len(options)})")
    print_step(f"완료. 모든 능력치를 성공적으로 추가했습니다.\n")
if 6 in RUN_STEP:
    add_stat()

conn.close()