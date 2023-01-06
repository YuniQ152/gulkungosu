from time import sleep
from difflib import SequenceMatcher
from jamo import h2j, j2hcj
import re, datetime, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates
from modules.database import *
from modules.get import *

def remove_special_character(s):
    return re.sub("[^\uAC00-\uD7A3\u3131-\u31630-9a-zA-Z\b]", "", s) # 가-힣 ㄱ-ㅣ 0-9 a-z A-Z 띄어쓰기

def separate_jamo(text):
    text = j2hcj(h2j(text)) # 한글을 자음과 모음으로 분리함 (파머모 -> ㅍㅏㅁㅓㅁㅗ)
    text = text.replace("ㅘ", "ㅗㅏ")
    text = text.replace("ㅙ", "ㅗㅐ")
    text = text.replace("ㅚ", "ㅗㅣ")
    text = text.replace("ㅝ", "ㅜㅓ")
    text = text.replace("ㅞ", "ㅜㅔ")
    text = text.replace("ㅟ", "ㅜㅣ")
    text = text.replace("ㅢ", "ㅡㅣ")
    return text

def separate_jaum(text):
    text = text.replace("ㄳ", "ㄱㅅ")
    text = text.replace("ㄵ", "ㄴㅈ")
    text = text.replace("ㄶ", "ㄴㅎ")
    text = text.replace("ㄺ", "ㄹㄱ")
    text = text.replace("ㄻ", "ㄹㅁ")
    text = text.replace("ㄽ", "ㄹㅅ")
    text = text.replace("ㄾ", "ㄹㅌ")
    text = text.replace("ㄿ", "ㄹㅍ")
    text = text.replace("ㅀ", "ㄹㅎ")
    text = text.replace("ㅄ", "ㅂㅅ")
    return text

def chosung(text):
    text = re.sub("[가-깋]", "ㄱ", text)
    text = re.sub("[까-낗]", "ㄲ", text)
    text = re.sub("[나-닣]", "ㄴ", text)
    text = re.sub("[다-딯]", "ㄷ", text)
    text = re.sub("[따-띻]", "ㄸ", text)
    text = re.sub("[라-맇]", "ㄹ", text)
    text = re.sub("[마-밓]", "ㅁ", text)
    text = re.sub("[바-빟]", "ㅂ", text)
    text = re.sub("[빠-삫]", "ㅃ", text)
    text = re.sub("[사-싷]", "ㅅ", text)
    text = re.sub("[싸-앃]", "ㅆ", text)
    text = re.sub("[아-잏]", "ㅇ", text)
    text = re.sub("[자-짛]", "ㅈ", text)
    text = re.sub("[짜-찧]", "ㅉ", text)
    text = re.sub("[차-칳]", "ㅊ", text)
    text = re.sub("[카-킿]", "ㅋ", text)
    text = re.sub("[타-팋]", "ㅌ", text)
    text = re.sub("[파-핗]", "ㅍ", text)
    text = re.sub("[하-힣]", "ㅎ", text)
    return text

def compute_match_ratio(input: str, db_dict: dict) -> float:
    """input과 아이템 이름이 얼마나 일치하는지 계산해서 리턴하는 함수"""
    id_ratio = 1 if db_dict['id'] == input else 0

    input = remove_special_character(input)

    en = remove_special_character(db_dict["name_en"])
    en_ratio = SequenceMatcher(None, input, en).ratio()
    
    ko = remove_special_character(db_dict["name_ko"])
    ko_ratio_byte = SequenceMatcher(None, input, ko).ratio()
    ko_ratio_jamo = SequenceMatcher(None, separate_jamo(input), separate_jamo(ko)).ratio()
    ko_proportion = min(50*math.log10(len(separate_jamo(ko))), 100)
    ko_ratio = ko_ratio_byte*ko_proportion/100 + (ko_ratio_jamo)*(100-ko_proportion)/100

    if db_dict['aliases'] is not None:
        aliases = remove_special_character(db_dict['aliases'])
        aliases_ratio_byte = SequenceMatcher(None, input, aliases).ratio()
        aliases_ratio_jamo = SequenceMatcher(None, separate_jamo(input), separate_jamo(aliases)).ratio()
        aliases_proportion = min(50*math.log10(len(separate_jamo(aliases))), 100)
        aliases_ratio = aliases_ratio_byte*aliases_proportion/100 + (aliases_ratio_jamo)*(100-aliases_proportion)/100
    else:
        aliases_ratio = 0

    if re.sub("[^ㄱ-ㅎ0-9\b]", "", input) == input:
        input_chosung = separate_jaum(input)
        chosung_ratio = SequenceMatcher(None, input_chosung, chosung(ko)).ratio()
    else:
        chosung_ratio = 0

    ratio = max(id_ratio, en_ratio, ko_ratio, aliases_ratio, chosung_ratio)
    return ratio

def search_db(input: str) -> list:
    items      = fetch_item_info_all()
    crops      = fetch_crop_info_all()
    facilities = fetch_facility_info_all()
    buffs      = fetch_buff_info_all()
    stats      = fetch_stat_info_all()
    db_list = []
    for i in items:
        i['type'] = 'item'
        db_list.append(i)
    for i in crops:
        i['type'] = 'crop'
        db_list.append(i)
    for i in facilities:
        i['type'] = 'facility'
        db_list.append(i)
    for i in buffs:
        i['type'] = 'buff'
        db_list.append(i)
    for i in stats:
        i['type'] = 'stat'
        db_list.append(i)

    for i in range(len(db_list)):
        db_list[i]['ratio'] = compute_match_ratio(input, db_list[i])
    db_list = sorted(db_list, key=lambda x:-x['ratio'])

    # for i in range(6):
    #     print(f"{db_list[i]['name_ko']} {db_list[i]['ratio']*100:.2f}%")
    # print(f"=============")

    return db_list

def add_ratio_in_dict(input: str, full_item_list: list, category = None, except_item: list = []) -> list:
    items = []
    for item in full_item_list:
        if category is None or item['category'] == category:
            if item['id'] not in except_item and item['name_ko'] not in except_item and item['name_en'] not in except_item:
                item['ratio'] = compute_match_ratio(input, item)
                items.append(item)
    items = sorted(items, key=lambda x:-x['ratio']) # ratio 내림차순으로 정렬

    return items

def get_item_quantity_from_inventory(inventory_item_list: list, item_id: str) -> int:
    """여행자 인벤토리에 특정 아이템이 얼마나 있는지 개수를 리턴하는 함수"""
    total_quantity = 0
    for i in range(len(inventory_item_list)):
        if inventory_item_list[i]["staticId"] == item_id:
            total_quantity += inventory_item_list[i]["quantity"]
    return total_quantity

def embed_color(ratio: float, reverse: bool = False) -> tuple:
    """1.0 = Green | 0.5 = Yellow | 0.0 = Red"""
    if not reverse:
        green  = [ 46, 204, 113]
        yellow = [241, 196,  15]
        red    = [231,  76,  60]
    else:
        red    = [ 46, 204, 113]
        yellow = [241, 196,  15]
        green  = [231,  76,  60]
    generated_color = []
    if ratio > 1:
        generated_color = green
    elif ratio < 0:
        generated_color = red
    elif ratio >= 0.5: # Green ~ Yellow
        ratio = (ratio-0.5)*2
        for i in range(3):
            generated_color.append(int(green[i]*ratio + yellow[i]*(1.0-ratio)))
    else: # Yellow ~ Red
        ratio = ratio*2
        for i in range(3):
            generated_color.append(int(yellow[i]*ratio + red[i]*(1.0-ratio)))
    return tuple(generated_color)

def generate_graph(x: list, y: list):
    plt.figure(figsize=(8, 4.5))
    plt.plot(x, y, alpha=1, linewidth=2)
    plt.xlim(x[0], datetime.datetime.now())
    plt.grid(True)
    ax = plt.gca()
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%m/%d"))
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    # ax.xaxis.set_minor_formatter(dates.DateFormatter("%H"))
    plt.savefig("trade.png", facecolor="#eeeeee", bbox_inches='tight', pad_inches=0.1, dpi=150)
    
def convert_datetime(unixtime):
    """Convert unixtime to datetime"""
    datetime_str = datetime.datetime.fromtimestamp(unixtime).strftime("%Y-%m-%d %H:%M:%S")
    datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    return datetime_obj

def convert_seconds_to_time_text(in_seconds: int) -> str: # Credit: https://blog.naver.com/wideeyed/221522740612
    t1   = datetime.timedelta(seconds=in_seconds)
    days = t1.days
    _sec = t1.seconds
    (hours, minutes, seconds) = str(datetime.timedelta(seconds=_sec)).split(':')
    hours   = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    
    result = []
    if days >= 1:
        result.append(str(days)+'일')
    if hours >= 1:
        result.append(str(hours)+'시간')
    if minutes >= 1:
        result.append(str(minutes)+'분')
    if seconds >= 1:
        result.append(str(seconds)+'초')
    result = ' '.join(result)
    return result

def arrow_number(num: int) -> str:
    text = ""
    if num > 0:
        text += "🔺"
    elif num < 0:
        text += "🔻"
    text += str(abs(num))
    return text

def api_error_message(response_code: int, member: discord.Member = None) -> str:
    if response_code == 401:
        return "(401) 오류: 인증에 실패했습니다. 문제가 계속되는 경우 고등어 서버에 "
    elif response_code == 403:
        return "(403) 오류: API 사용자의 계정이 아닙니다."
    elif response_code == 404:
        if member is None:
            return "(404) 그런 서버는 없습니다."
        else:
            return f"(404) {member.mention}님은 파머모 유저가 아닙니다."
    elif response_code == 406:
        if member is None:
            return "(406) 이 아이템은 만들 수 없습니다."
        else:
            return f"(406) {member.mention}님이 API 정보 활용을 거부하여 정보를 조회할 수 없습니다."
    elif response_code == 412:
        return "(412) 오류: 요청 형식 검증을 실패했습니다."
    elif response_code == 416:
        return "(416) 푯말의 내용이 너무 길어요! 100글자 이내로 줄여주세요."
    elif response_code == 429:
        return "(429) 오류: 가스가 부족합니다. 몇 초 후에 다시 시도해주세요."
    elif response_code == 504:
        return "(504) 오류: 파머모가 오프라인일 수 있습니다"
    else:
        return f"({response_code}) 오류: 알 수 없음"

def item_category_to_text(category: str, abbreviation: bool = False) -> str:
    if category == "box":
        return "상자"
    elif category == "crop":
        return "작물"
    elif category == "document":
        return "문서"
    elif category == "element":
        return "원소"
    elif category == "equipment-a":
        if abbreviation: return "허리"
        else:            return "장비: 허리"
    elif category == "equipment-b":
        if abbreviation: return "하의"
        else:            return "장비: 하의"
    elif category == "equipment-h":
        if abbreviation: return "모자"
        else:            return "장비: 모자"
    elif category == "equipment-k":
        if abbreviation: return "등"
        else:            return "장비: 등"
    elif category == "equipment-m":
        if abbreviation: return "훈장"
        else:            return "장비: 훈장"
    elif category == "equipment-o":
        if abbreviation: return "신발"
        else:            return "장비: 신발"
    elif category == "equipment-s":
        if abbreviation: return "방패"
        else:            return "장비: 방패"
    elif category == "equipment-t":
        if abbreviation: return "상의"
        else:            return "장비: 상의"
    elif category == "equipment-w":
        if abbreviation: return "무기"
        else:            return "장비: 무기"
    elif category == "etc":
        return "기타"
    elif category == "food":
        return "음식"
    elif category == "resource":
        return "자원"
    elif category == "sapling":
        return "묘목"
    else:
        return "알 수 없음"

def crop_characteristic_to_text(characteristic: str) -> str:
    if characteristic == "low":
        return "낮음"
    elif characteristic == "medium":
        return "중간"
    elif characteristic == "high":
        return "높음"
    elif characteristic == "slower":
        return "매우 느림"
    elif characteristic == "slow":
        return "느림"
    elif characteristic == "average":
        return "보통"
    elif characteristic == "fast":
        return "빠름"
    else:
        return "알 수 없음"