import os, requests, json, sqlite3, time
from dotenv import load_dotenv

load_dotenv()

def db_item() -> None:

    def get_item(item_name: str) -> dict:
        url = "https://farm.jjo.kr/api/static/item/" + str(item_name)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)
        
        item = {}
        item |= {"id": content['data']['id']}
        item |= {"icon": content['data']['icon']}
        item |= {"name": content['names']['ko']}
        item |= {"description": content['descriptions']['ko'].replace("<:blue_haired_moremi:923442506195173456>", "<:blue_haired_moremi:1122898278313377893>")}
        item |= {"category": content['data']['category']}
        item |= {"level": content['data']['level']}
        item |= {"weight": content['data']['weight']}
        item |= {"vested": 1} if content['data']['vested'] else {"vested": 0}
        item |= {"planted": 1} if content['data']['planted'] else {"planted": 0}
        item |= {"usable": 1} if content['data']['usable'] else {"usable": 0}
        item |= {"collectible": 1} if content['data']['collectible'] else {"collectible": 0}
        item |= {"options": content['data']['options']} if content['data']['options'] else {"options": None}
        if content['data']['options'] is not None:
            item |= {"coupon": content['data']['options']['coupon']} if "coupon" in content['data']['options'] else {"coupon": None}
        else:
            item |= {"coupon": None}

        return item

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
        name TEXT,
        description TEXT,
        category TEXT,
        level INTEGER,
        weight INTEGER,
        vested INTEGER,
        planted INTEGER,
        usable INTEGER,
        collectible INTEGER,
        options TEXT,
        coupon TEXT,
        craftables TEXT,
        ingredients TEXT,
        steps TEXT,
        aliases TEXT,
        comments TEXT
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
        cur.execute("INSERT OR REPLACE INTO item(id, icon, name, description, category, level, weight, vested, planted, usable, collectible, options, coupon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", insert_list)
        if "aliases" in items[i]:
            cur.execute(f"UPDATE item SET aliases=? WHERE id=?", (str(items[i]['aliases']), item_id))

        response_code, craftables, ingredients, steps = get_item_recipe(item_id)
        if response_code == 200:
            cur.execute("UPDATE item SET craftables=?, ingredients=?, steps=? WHERE id=?", (str(craftables), str(ingredients), str(steps), item_id))
            print(f"[{item['icon']} {item['name']}] 아이템 및 제작 방법 추가됨. ({i+1}/{len(items)})")
        elif response_code == 406:
            print(f"[{item['icon']} {item['name']}] 아이템 추가됨. 제작 방법 없음. ({i+1}/{len(items)})")

        conn.commit()
        time.sleep(1)

    print(f"완료. 모든 아이템을 성공적으로 추가했습니다.\n")
    conn.close()


def db_crop() -> None:

    def get_crop_info(crop_id: str) -> dict:
        url = "https://farm.jjo.kr/api/static/crop/" + str(crop_id)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)

        crop = {}
        crop |= {"id": content['data']['id']}
        crop |= {"icon": content['data']['icon']}
        crop |= {"name": content['names']['ko']}
        crop |= {"description": content['descriptions']['ko'].replace("<:blue_haired_moremi:923442506195173456>", "<:blue_haired_moremi:1122898278313377893>")}
        crop |= {"is_tree": 1} if content['data']['isTree'] else {"is_tree": 0}
        crop |= {"level": content['data']['level']}
        crop |= {"strawberry": content['data']['strawberry']}
        crop |= {"growth": content['data']['characteristics']['growth']}
        crop |= {"water": content['data']['characteristics']['water']}
        crop |= {"soil": content['data']['characteristics']['soil']}
        crop |= {"health": content['data']['characteristics']['health']}
        return crop

    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS crop(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name TEXT,
        description TEXT,
        is_tree INTEGER,
        level INTEGER,
        strawberry INTEGER,
        growth TEXT,
        water TEXT,
        soil TEXT,
        health TEXT,
        aliases TEXT,
        comments TEXT
        )""")
    conn.commit()
    
    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    crops = data['crop']
    
    for i in range(len(crops)):

        crop_id = crops[i]['id']
        crop = get_crop_info(crop_id)

        insert_list = list(crop.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO crop(id, icon, name, description, is_tree, level, strawberry, growth, water, soil, health) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (insert_list))
        if "aliases" in crops[i]:
            cur.execute(f"UPDATE crop SET aliases=? WHERE id=?", (str(crops[i]['aliases']), crop_id))
        conn.commit()
        print(f"[{crop['icon']} {crop['name']}] 작물 추가됨. ({i+1}/{len(crops)})")
        time.sleep(0.15)

    print(f"완료. 모든 작물을 성공적으로 추가했습니다.\n")
    conn.close()


def db_facility():

    def get_facility_info(facility_id: str) -> dict:
        url = "https://farm.jjo.kr/api/static/facility/" + str(facility_id)
        response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
        content = json.loads(response.content)
    
        facility = {}
        facility |= {"id": content['data']['id']}
        facility |= {"icon": content['data']['icon']}
        facility |= {"name": content['names']['ko']}
        facility |= {"description": content['descriptions']['ko'].replace("<:blue_haired_moremi:923442506195173456>", "<:blue_haired_moremi:1122898278313377893>")}
        facility |= {"color": content['data']['color']}
        facility |= {"level": content['data']['level']}
        facility |= {"size": content['data']['size']} if "size" in content['data'] else {"size": None}
        facility |= {"rotatable": 1} if content['data']['rotatable'] else {"rotatable": 0}
        facility |= {"build_costs": content['data']['buildCosts']}
        facility |= {"options": content['data']['options']}
        return facility

    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS facility(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name TEXT,
        description TEXT,
        color TEXT,
        level INTEGER,
        size TEXT,
        rotatable INTEGER,
        build_costs TEXT,
        options TEXT,
        aliases TEXT,
        comments TEXT
        )""")
    conn.commit()
    
    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    facilities = data['facility']
    
    for i in range(len(facilities)):

        facility_id = facilities[i]['id']
        facility = get_facility_info(facility_id)

        insert_list = list(facility.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO facility(id, icon, name, description, color, level, size, rotatable, build_costs, options) VALUES (?,?,?,?,?,?,?,?,?,?)", (insert_list))
        if "aliases" in facilities[i]:
            cur.execute(f"UPDATE facility SET aliases=? WHERE id=?", (str(facilities[i]['aliases']), facility_id))
        conn.commit()
        print(f"[{facility['icon']} {facility['name']}] 시설물 추가됨. ({i+1}/{len(facilities)})")
        time.sleep(0.15)

    print(f"완료. 모든 시설물을 성공적으로 추가했습니다.\n")
    conn.close()


def db_buff():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS buff(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name TEXT,
        description TEXT,
        options TEXT,
        aliases TEXT,
        comments TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    buffs = data['buff']

    for i in range(len(buffs)):
        buff = buffs[i]
        buff_id = buff['id']

        insert_list = list(buff.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO buff(id, icon, name, description, options, aliases) VALUES (?,?,?,?,?,?)", (insert_list))
        if "aliases" not in buff or buff['aliases'] is None:
            cur.execute(f"UPDATE buff SET aliases=NULL WHERE id=?", (buff_id, ))
        conn.commit()
        print(f"[{buff['icon']} {buff['name']}] 버프 추가됨. ({i+1}/{len(buffs)})")

    print(f"완료. 모든 버프를 성공적으로 추가했습니다.\n")
    conn.close()


def db_option():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS option(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name TEXT,
        description TEXT,
        aliases TEXT,
        comments TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    options = data['option']

    for i in range(len(options)):
        option = options[i]
        option_id = option['id']

        insert_list = list(option.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO option(id, icon, name, description, aliases) VALUES (?,?,?,?,?)", (insert_list))
        if "aliases" not in option or option['aliases'] is None:
            cur.execute(f"UPDATE buff SET aliases=NULL WHERE id=?", (option_id, ))
        conn.commit()
        print(f"[{option['icon']} {option['name']}] 속성 추가됨. ({i+1}/{len(options)})")

    print(f"완료. 모든 속성을 성공적으로 추가했습니다.\n")
    conn.close()


def db_step():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS step(
        id TEXT PRIMARY KEY,
        icon TEXT,
        name TEXT,
        description TEXT,
        aliases TEXT,
        comments TEXT
        )""")
    conn.commit()

    with open("getdata.json", "rt", encoding="UTF-8") as file:
        data = json.load(file)

    steps = data['step']

    for i in range(len(steps)):
        step = steps[i]
        step_id = step['id']

        insert_list = list(step.values())
        for j in range(len(insert_list)):
            if insert_list[j] is not None:
                insert_list[j] = str(insert_list[j])
        cur.execute("INSERT OR REPLACE INTO step(id, icon, name, description, aliases) VALUES (?,?,?,?,?)", (insert_list))
        if "aliases" not in step or step['aliases'] is None:
            cur.execute(f"UPDATE buff SET aliases=NULL WHERE id=?", (step_id, ))
        conn.commit()
        print(f"[{step['icon']} {step['name']}] 제작 과정 추가됨. ({i+1}/{len(steps)})")

    print(f"완료. 모든 제작 과정을 성공적으로 추가했습니다.\n")
    conn.close()


def db_comment():
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    conn.execute("""CREATE TABLE IF NOT EXISTS item_comment(
        comment_id INTEGER PRIMARY KEY AUTOINCREMENT
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        display_name TEXT NOT NULL,
        content TEXT NOT NULL,
        upvote TEXT DEFAULT "[]",
        downvote TEXT DEFAULT "[]",
        created_at INTEGER,
        is_edited INTEGER DEFAULT 0,
        is_deleted INTEGER DEFAULT 0,
        FOREIGN KEY (item_id) REFERENCES item(id)
        )""")
    conn.commit()

    print(f"완료. 코멘트 테이블을 추가했습니다.\n")
    conn.close()



db_item()
db_crop()
db_facility()
db_buff()
db_option()
db_step()
# db_comment()
