import os, requests, json
from dotenv import load_dotenv

load_dotenv()

def get_cofarm_channel_id(server_id: int):
    url = "https://farm.jjo.kr/api/guild/" + str(server_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        cofarms = json.loads(response.content)["cofarms"]
        cofarm_channel_id = []
        for i in range(len(cofarms)):
            cofarm_channel_id.append(int(cofarms[i]["id"]))
        return(response.status_code, cofarm_channel_id)
    else:
        return(response.status_code, None)

def get_cofarm_info(server_id, channel_id):
    url = "https://farm.jjo.kr/api/guild/" + str(server_id) + "/cofarm/" + str(channel_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        farms         = json.loads(response.content)["farms"]
        contributions = json.loads(response.content)["contributions"]
        return(response.status_code, farms, contributions)
    else:
        return(response.status_code, None, None)

def get_user_id(server, discord_id):
    url = "https://farm.jjo.kr/api/link/by-discord/" + str(server) + "/" + str(discord_id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        user_id = json.loads(response.content)["id"]
        return(response.status_code, user_id)
    else:
        return(response.status_code, None)

def get_user_info(id):
    url = "https://farm.jjo.kr/api/link/" + str(id)
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        data = json.loads(response.content)["data"]
        return(response.status_code, data)
    else:
        return(response.status_code, None)

def get_user_farm(id):
    url = "https://farm.jjo.kr/api/link/" + str(id) + "/farms"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        farm = json.loads(response.content)["list"]
        return(response.status_code, farm)
    else:
        return(response.status_code, None)

def get_user_farm(id):
    url = "https://farm.jjo.kr/api/link/" + str(id) + "/farms"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        farm = json.loads(response.content)["list"]
        return(response.status_code, farm)
    else:
        return(response.status_code, None)

def get_user_inventory(id):
    url = "https://farm.jjo.kr/api/link/" + str(id) + "/items"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        data = json.loads(response.content)
        weight = data["weight"]
        max_weight = data["maxWeight"]
        item_list = data["list"]
        return response.status_code, weight, max_weight, item_list
    else:
        return response.status_code, None, None, None

def get_user_land(id):
    url = "https://farm.jjo.kr/api/link/" + str(id) + "/land"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        data = json.loads(response.content)
        size = data["size"]
        facilities = data["facilities"]
        return response.status_code, size, facilities
    else:
        return response.status_code, None, None

def get_user_equipment(id):
    url = "https://farm.jjo.kr/api/link/" + str(id) + "/equipment"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        data = json.loads(response.content)
        equipments = data["list"]
        return response.status_code, equipments
    else:
        return response.status_code, None

def get_crop_trade_history(crop_id):
    url = "https://farm.jjo.kr/api/stock/" + str(crop_id) + "/recent"
    response = requests.get(url, headers={"Authorization": os.getenv("BHMO_API_TOKEN")})
    if response.status_code == 200:
        data = json.loads(response.content)['list']
        return response.status_code, data
    else:
        return response.status_code, None