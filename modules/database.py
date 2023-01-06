import sqlite3
from ast import literal_eval

conn = sqlite3.connect("db.sqlite3")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def fetch_item_info(item_id):
    cur.execute("SELECT * FROM item WHERE id = ?", (item_id, ))
    row = dict(cur.fetchone()) # {'id': 'brick', 'icon': '🧱', 'category': 'etc', 'level': 5, ...}
    if row['options']     is not None: row['options']     = literal_eval(row['options'])
    if row['craftables']  is not None: row['craftables']  = literal_eval(row['craftables'])
    if row['ingredients'] is not None: row['ingredients'] = literal_eval(row['ingredients'])
    if row['steps']       is not None: row['steps']       = literal_eval(row['steps'])
    return row
def fetch_item_info_all():
    cur.execute("SELECT * FROM item")
    rows = cur.fetchall()
    item_list = [dict(rows[i]) for i in range(len(rows))] # [{...}, {...}, {...}, ...]
    for row in item_list:
        if row['options']     is not None: row['options']     = literal_eval(row['options'])
        if row['craftables']  is not None: row['craftables']  = literal_eval(row['craftables'])
        if row['ingredients'] is not None: row['ingredients'] = literal_eval(row['ingredients'])
        if row['steps']       is not None: row['steps']       = literal_eval(row['steps'])
    return item_list

def fetch_crop_info(crop_id):
    cur.execute("SELECT * FROM crop WHERE id = ?", (crop_id, ))
    row = dict(cur.fetchone())
    return row
def fetch_crop_info_all():
    cur.execute("SELECT * FROM crop")
    rows = cur.fetchall()
    crop_list = [dict(rows[i]) for i in range(len(rows))] # [{...}, {...}, {...}, ...]
    return crop_list

def fetch_facility_info(facility_id):
    cur.execute("SELECT * FROM facility WHERE id = ?", (facility_id, ))
    row = dict(cur.fetchone())
    if row['size']        is not None: row['size']        = literal_eval(row['size'])
    if row['build_costs'] is not None: row['build_costs'] = literal_eval(row['build_costs'])
    if row['options']     is not None: row['options']     = literal_eval(row['options'])
    return row
def fetch_facility_info_all():
    cur.execute("SELECT * FROM facility")
    rows = cur.fetchall()
    facility_list = [dict(rows[i]) for i in range(len(rows))] # [{...}, {...}, {...}, ...]
    for row in facility_list:
        if row['size']        is not None: row['size']        = literal_eval(row['size'])
        if row['build_costs'] is not None: row['build_costs'] = literal_eval(row['build_costs'])
        if row['options']     is not None: row['options']     = literal_eval(row['options'])
    return facility_list

def fetch_buff_info(buff_id):
    cur.execute("SELECT * FROM buff WHERE id = ?", (buff_id, ))
    row = dict(cur.fetchone())
    if row['options'] is not None: row['options'] = literal_eval(row['options'])
    return row
def fetch_buff_info_all():
    cur.execute("SELECT * FROM buff")
    rows = cur.fetchall()
    buff_list = [dict(rows[i]) for i in range(len(rows))] # [{...}, {...}, {...}, ...]
    for row in buff_list:
        if row['options'] is not None: row['options'] = literal_eval(row['options'])
    return buff_list

def fetch_stat_info(stat_id):
    cur.execute("SELECT * FROM stat WHERE id = ?", (stat_id, ))
    row = dict(cur.fetchone())
    return row
def fetch_stat_info_all():
    cur.execute("SELECT * FROM stat")
    rows = cur.fetchall()
    stat_list = [dict(rows[i]) for i in range(len(rows))] # [{...}, {...}, {...}, ...]
    return stat_list