import os, requests, json, sqlite3, time
from dotenv import load_dotenv

load_dotenv()

def db_item() -> None:

    def get_item(item_name: str) -> dict:
        url = "https://farm.jjo.kr/api/static/item/" + str(item_name)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)
        data = content['data']
        data |= {"name_ko": content['names']['ko']}
        data |= {"name_en": content['names']['en']}
        data |= {"descriptions_ko": content['descriptions']['ko']}
        data |= {"descriptions_en": content['descriptions']['en']}
        return data

    def get_item_recipe(item_id: str) -> dict:
        url = "https://farm.jjo.kr/api/static/recipe/" + str(item_id)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        if response.status_code == 200:
            content = json.loads(response.content)
            craftables = content["craftables"]
            ingredients = content["ingredients"]
            steps = content["steps"]
            return response.status_code, craftables, ingredients, steps
        elif response.status_code == 406:
            return response.status_code, None, None, None

    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS item(
        id TEXT PRIMARY KEY,
        icon TEXT,
        category TEXT,
        level INTEGER,
        weight INTEGER,
        options TEXT,
        basic_stats TEXT,
        stats TEXT,
        health TEXT,
        buffs TEXT,
        coupon TEXT,
        etc TEXT,
        vested INTEGER,
        planted INTEGER,
        usable INTEGER,
        collectible INTEGER,
        name_ko TEXT,
        name_en TEXT,
        description_ko TEXT,
        description_en TEXT,
        craftables TEXT,
        ingredients TEXT,
        steps TEXT,
        aliases TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    items = data['item']
    for i in range(len(items)):

        item = get_item(items[i]['name'])
        item_id = item['id']

        insert_list = list(item.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
                if insert_list[j] == "True":
                    insert_list[j] = 1
                elif insert_list[j] == "False":
                    insert_list[j] = 0
        cur.execute("INSERT OR REPLACE INTO item(id, icon, category, level, weight, options, vested, planted, usable, collectible, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", insert_list)
        if "aliases" in items[i]:
            cur.execute(f"UPDATE item SET aliases=? WHERE id=?", (str(items[i]['aliases']), item_id))


        option_keys = {'basic_stats': ['ferocity', 'mentality', 'agility', 'tenacity', 'harmonicity'],
                       'stats': ['pf', 'mf', 'pr', 'mr', 'speed', 'concentration'],
                       'health': ['healAcceleration', 'divisibleHealth', 'health', 'maxHealth'],
                       'buffs': ['buffByEating', 'buffByUsing'],
                       'coupon': ['coupon'],
                       'etc': ['rainResistance', 'capacity', 'lifespan', 'expiredAt']}


        if item['options'] is not None:
            for k in option_keys:
                v = option_keys[k]
                d = {}
                for j in v:
                    if j in item['options']:
                        d |= {j: item['options'][j]}
                        print(item_id, k, j, item['options'][j], d)
                if len(d) != 0:
                    cur.execute(f"UPDATE item SET {k}=? WHERE id=?", (str(d), item_id))

        response_code, craftables, ingredients, steps = get_item_recipe(item_id)
        if response_code == 200:
            cur.execute("UPDATE item SET craftables=?, ingredients=?, steps=? WHERE id=?", (str(craftables), str(ingredients), str(steps), item_id))
            print(f"[{item['icon']} 아이템 및 제작 방법 추가됨. ({i+1}/{len(items)})")
        elif response_code == 406:
            print(f"[{item['icon']} 아이템 추가됨. 제작 방법 없음. ({i+1}/{len(items)})")

        conn.commit()
        time.sleep(1)
    print(f"완료. 모든 아이템을 성공적으로 추가했습니다.\n")

    conn.close()


def db_crop() -> None:

    def get_crop_info(crop_id: str) -> dict:
        url = "https://farm.jjo.kr/api/static/crop/" + str(crop_id)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)
        data = content['data']
        data['isTree'] = 1 if data['isTree'] is True else 0
        data |= data['characteristics']
        data |= {"name_ko": content['names']['ko']}
        data |= {"name_en": content['names']['en']}
        data |= {"descriptions_ko": content['descriptions']['ko']}
        data |= {"descriptions_en": content['descriptions']['en']}
        del data['characteristics']
        return data

    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS crop(
        id TEXT PRIMARY KEY,
        icon TEXT,
        level INTEGER,
        strawberry INTEGER,
        is_tree INTEGER,
        growth TEXT,
        water TEXT,
        soil TEXT,
        health TEXT,
        name_ko TEXT,
        name_en TEXT,
        description_ko TEXT,
        description_en TEXT,
        aliases TEXT
        )""")
    conn.commit()
    
    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    crops = data['crop']
    
    for i in range(len(crops)):

        crop_id = crops[i]['id']
        crop = get_crop_info(crop_id)
        print(crop)

        insert_list = list(crop.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO crop(id, icon, level, strawberry, is_tree, growth, water, soil, health, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (insert_list))
        if "aliases" in crops[i]:
            cur.execute(f"UPDATE crop SET aliases=? WHERE id=?", (str(crops[i]['aliases']), crop_id))
        conn.commit()

    conn.close()


def db_facility():

    def get_facility_info(facility_id: str) -> dict:
        url = "https://farm.jjo.kr/api/static/facility/" + str(facility_id)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)
        data = {'id': None, 'icon': None, 'color': None, 'level': None, 'size': None}
        data |= content['data']
        data |= {"name_ko": content['names']['ko']}
        data |= {"name_en": content['names']['en']}
        data |= {"descriptions_ko": content['descriptions']['ko']}
        data |= {"descriptions_en": content['descriptions']['en']}
        return data

    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS facility(
        id TEXT PRIMARY KEY,
        icon TEXT,
        color TEXT,
        level INTEGER,
        size TEXT,
        build_costs TEXT,
        options TEXT,
        rotatable INTEGER,
        name_ko TEXT,
        name_en TEXT,
        description_ko TEXT,
        description_en TEXT,
        aliases TEXT
        )""")
    conn.commit()
    
    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    facilities = data['facility']
    
    for i in range(len(facilities)):

        facility_id = facilities[i]['id']
        facility = get_facility_info(facility_id)
        # if "size" not in facility:  #
        #     facility['size'] = None #
        print(facility)

        insert_list = list(facility.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO facility(id, icon, color, level, size, build_costs, options, rotatable, name_ko, name_en, description_ko, description_en) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (insert_list))
        if "aliases" in facilities[i]:
            cur.execute(f"UPDATE facility SET aliases=? WHERE id=?", (str(facilities[i]['aliases']), facility_id))
        conn.commit()

    conn.close()

def db_buff():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS buff(
        id TEXT PRIMARY KEY,
        icon TEXT,
        options TEXT,
        name_ko TEXT,
        name_en TEXT,
        description_ko TEXT,
        description_en TEXT,
        aliases TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    buffs = data['buff']

    for i in range(len(buffs)):
        buff = buffs[i]
        buff_id = buff['id']
        print(buff)

        insert_list = list(buff.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO buff(id, icon, options, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?,?)", (insert_list))
        if "aliases" not in buff or buff['aliases'] is None:
            cur.execute(f"UPDATE buff SET aliases=NULL WHERE id=?", (buff_id, ))
        conn.commit()

    conn.close()

def db_stat():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS stat(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name_ko TEXT,
        name_en TEXT,
        description_ko TEXT,
        description_en TEXT,
        aliases TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    stats = data['option']

    for i in range(len(stats)):
        stat = stats[i]
        stat_id = stat['id']
        print(stat)

        insert_list = list(stat.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO stat(id, icon, name_ko, name_en, description_ko, description_en, aliases) VALUES (?,?,?,?,?,?,?)", (insert_list))
        if "aliases" not in stat or stat['aliases'] is None:
            cur.execute(f"UPDATE buff SET aliases=NULL WHERE id=?", (stat_id, ))
        conn.commit()

    conn.close()



db_item()
db_crop()
db_facility()
db_buff()
db_stat()