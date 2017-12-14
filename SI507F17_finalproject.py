import requests
import json
import sys
from boss import Boss
from loot import Loot
from secret import API_KEY
from datetime import datetime
from bs4 import BeautifulSoup
import os
import psycopg2
import psycopg2.extras
import codecs

# functions borrowed from project 5 to set timestamp to cache and check if
# the cache is outdated

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
boss_cache_file = "boss_data.json"
loot_cache_file = "loot_data.json"
conn = ""
cur = ""
global_boss_list = []


def db_connect_cursor():
    '''
    Function borrowed from project 6 to setup databse connection
    '''
    try:
        db_connection = psycopg2.connect("dbname='wow_loot'")
        print("Success connecting to database")
    except:
        print("Unable to connect to the database")
        sys.exit(1)

    db_cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

conn, cur = db_connect_cursor()


def write_time_stamp(input, expire_in_days):
    '''
    Function to write time stamp and expiration time
    @params:
        input: dict data
        expire_in_days: int
    @return:
        None
    '''
    input["time_stamp"] = datetime.now().strftime(DATETIME_FORMAT)
    input["expire_in_days"] = expire_in_days


def is_expired(input):
    '''
    Function to check if cached data is expired
    @params:
        input: dict data
    @return:
        Boolean
    '''
    now = datetime.now()
    try:
        time_stamp = datetime.strptime(input["time_stamp"], DATETIME_FORMAT)
        expire_in_days = input["expire_in_days"]
        delta = now - time_stamp
        delta_in_days = delta.days

        if delta_in_days > expire_in_days:
            return True
        else:
            return False
    except:
        print("No time info in the provided input, please run write_time_stamp() first")
        return False


def load_cache(filename):
    '''
    Function to load data of all the zones from cachefile
    @param:
        filename: str filename of the cache file
    @return:
        dict json data
    '''

    try:
        with open(filename, "r") as f:
            cache_data = f.read()
            data = json.loads(cache_data)
            # check if data is expired
            if is_expired(data):
                raise Exception

            return data
    except:
        return set_cache(filename)


def load_boss_cache(url, filename=boss_cache_file):
    '''
    Load certain HTML of the boss from boss_data.json, or set the information in cache if not exists or has expired
    @params:
        url: str
    @return:
        str HTML content
    '''
    # print(url)
    data = {}
    try:
        with open(filename, "r") as f:
            cache_data = f.read()
            data = json.loads(cache_data)
            # check if data is expired
            boss_data = data[url]
            if is_expired(boss_data):
                raise Exception

            return boss_data['html']
    except:
        return set_boss_cache(url, data, filename)


def set_boss_cache(url, data, filename=boss_cache_file):
    '''
    Function to request data of certain boss from wowdb and save html text with time stamp
    @param:
        url: str
        data: dict current cached data
    @return:
        str HTML content
    '''
    new_data = requests.get(url).text
    data['url'] = {
        'html': new_data
    }
    write_time_stamp(data['url'], 365)
    with open(filename, 'w') as f:
        cache_json = json.dumps(data)
        f.write(cache_json)
    return new_data


def load_loot_cache(loot_id, filename=loot_cache_file):
    '''
    Load certain HTML of the boss from loot_data.json, or set the information in cache if not exists or has expired
    @params:
        url: str
    @return:
        dict of a single loot
    '''
    data = {}
    try:
        with open(filename, "r") as f:
            cache_data = f.read()
            data = json.loads(cache_data)
            # check if data is expired
            loot_data = data[loot_id]
            if is_expired(loot_data):
                raise Exception

            return loot_data
    except:
        return set_loot_cache(loot_id, data, filename)


def set_loot_cache(loot_id, data, filename=loot_cache_file):
    '''
    Function to get loot info via Blizzard API, set in cache and return a loot object
    @params:
        loot_id: str
        data: dict current cached data
    @return:
        dict of a single loot
    '''
    url = "https://us.api.battle.net/wow/item/{0}?locale=en_US&apikey={1}".format(
        loot_id, API_KEY)
    new_data = json.loads(requests.get(url).text)

    data[loot_id] = new_data
    # print(data[loot_id])
    write_time_stamp(data[loot_id], 30)
    with open(filename, 'w') as f:
        cache_json = json.dumps(data)
        f.write(cache_json)
    return new_data


def set_cache(filename):
    '''
    Function to request data of all the zones and save in cachefile
    @param: str filename of the cache file
    @return: dict json data
    '''
    data = json.loads(requests.get(
        "https://us.api.battle.net/wow/zone/?locale=en_US&apikey={}".format(API_KEY)).text)
    write_time_stamp(data, 2)
    with open(filename, 'w') as f:
        f.write(json.dumps(data))
    return data


def clean_cache():
    '''
    Funtion to delete all the cached file
    @param: none
    @return: none
    '''
    try:
        os.remove("all_zones.json")
        print("Successfully cleared zone caches!")
    except:
        print("No zone cache file to clear")
    try:
        os.remove("boss_data.json")
        print("Successfully cleared boss caches!")
    except:
        print("No boss cache file to clear")
    try:
        os.remove("loot_data.json")
        print("Successfully cleared loot caches!")
    except:
        print("No loot cache file to clear")
# O(n) search


def search_zones(search_term):
    '''
    Search the zone based on input
    Search flow: Get zones info from zones list, get bosses info from zones info,
                 get item list from wowdb using bosses info, get item info from Blizzard API
    @params:
        search_term: string, name of the zone
    @return:
        list of Boss objects
    '''
    # startTime = datetime.now()

    dic = load_cache("all_zones.json")
    res = None
    for i in dic["zones"]:
        if i["urlSlug"] == search_term:
            res = i
    if not res:
        print("Zone you searched does not exist.")
        return
    # print(res)
    boss_list = []
    loot_list = []
    zoneID = res['id']
    zone = res['name']
    for i in res['bosses']:
        name = i['name']
        ID = i['id']
        npc = []
        if len(i['npcs']) > 1:
            for j in i['npcs']:
                npc.append(j['id'])
        else:
            npc = [ID]
        level = i['level']
        level_heroic = i['heroicLevel']
        try:
            description = i['description']
        except:
            description = "N/A"

        boss = Boss(
            name,
            ID,
            npc,
            level,
            level_heroic,
            zoneID,
            zone,
            description)
        boss_list.append(boss)

    for i in boss_list:
        loots = search_loot(i)
        loot_list += loots
        for j in loots:
            i.add_loot(j)

    add_to_database(boss_list, "boss")
    add_to_database(loot_list, "loot")
    print("Search complete and results have been appended to database")
    write_for_flask(boss_list)

    # timeElapsed = datetime.now() - startTime
    # print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))


def write_for_flask(global_boss_list):
    master_list = []
    for i in global_boss_list:
        temp_dict = {
            "name": i.name,
            "description": i.description,
            "loot": []
        }
        for j in i.lootList:
            loot_dict = {
                "name": j.name,
                "ilevel": j.ilevel,
                "stats": j.stats_to_string(),
                "spell": j.spell
            }
            temp_dict['loot'].append(loot_dict)
        master_list.append(temp_dict)
    data = {"data": master_list, "zone": global_boss_list[0].zone}
    with open("flask_data.json", 'w') as f:
        json_data = json.dumps(data)
        f.write(json_data)


def search_loot(boss):
    '''
    Search loot based on boss_id on wowdb
    Search flow: Get loot list using boss_id on wowdb, get list of loot pages,
                 pass the BeautifulSoup object of the pages to scrap_loot(bs)
                 get a list of item_ids from scrap_loot(bs)
                 search item info from Blizzard API
                 return a list of loot objects
    @params:
        boss: boss object
    @return:
        list of Loot objects
    '''

    boss_id = boss.npc
    loot_id_list = []
    print("Search loots for " + str(boss_id[0]))
    base_url = "http://www.wowdb.com/npcs/"
    bs = BeautifulSoup(
        load_boss_cache(
            base_url + str(boss_id[0])),
        "html.parser")
    trial = scrap_loot(bs)
    if not trial:
        for i in range(1, len(boss_id)):
            bs = BeautifulSoup(
                load_boss_cache(
                    base_url + str(boss_id[i])),
                "html.parser")
            trial = scrap_loot(bs)
            if trial:
                break

    loot_id_list += trial
    page_list = bs.find(
        "ul", {
            "class": "b-pagination-list paging-list j-tablesorter-pager j-listing-pagination"})
    if page_list:
        pages = page_list.find_all("a", {"class": "b-pagination-item"})
        page_url = []
        for i in pages:
            page_url.append("http://www.wowdb.com" + i['href'])
        for i in page_url:
            loot_id_list += scrap_loot(BeautifulSoup(load_boss_cache(i),
                                                     "html.parser"))
    # print(loot_id_list)
    # print(len(loot_id_list))
    res_loot_list = []
    for i in loot_id_list:
        loot = get_loot_info(i, str(boss_id[0]))
        if loot:
            res_loot_list.append(loot)
    return res_loot_list


def get_loot_info(loot_id, boss_id):
    '''
    Function to get loot info via Blizzard API and return a loot object
    @params:
        loot_id: str
        boss_id: str
    @return:
        Loot object
    '''
    data = load_loot_cache(loot_id)
    stats = {}
    spell = {}
    try:
        name = data['name']
    except:
        return None
    try:
        stats = data['bonusStats']
    except:
        stats = []
    try:
        spell = data['itemSpells']
    except:
        spell = []
    res = Loot(
        data['name'],
        data['id'],
        data['itemLevel'],
        boss_id,
        stats,
        spell,
        data['description'])
    return res


def scrap_loot(bs):
    '''
    Scrap BeautifulSoup object of loot page from wowdb and return loot list to a list of item_ids
    @params:
        bs: BeautifulSoup loot page
    @return:
        list of item_ids
    '''
    res = []
    try:
        table = bs.find("div", {"id": "tab-drops-item"})
        items = table.find_all("td", {"class": "col-name"})
    except:
        return []
    for i in items:
        link = i.find("a", {"class": "t"})['href']
        link = link[link.find("items") + 6:link.find('-')]
        res.append(link)

    return res


def setup_database():
    '''
    Set up 2 tables in SQL database: Boss and Loot
    Boss: Name, ID, Level, Level_Heroic, Level_Heroic_Repr, Zone, Description
    Loot: Name, ID, Boss_ID as foreign key,
    '''

    cur.execute(
        """CREATE TABLE IF NOT EXISTS "Boss"("Name" VARCHAR(40) UNIQUE, "ID" INT UNIQUE, "Level" INT, "Level_Heroic" INT, "Level_Heoic_Repr" VARCHAR(10), "Zone" INT, "Description" TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Loot"("Name" VARCHAR(128), "ID" INT UNIQUE,
                    "Item_Level" INT,
                    "Boss_ID" INT, FOREIGN KEY ("Boss_ID") REFERENCES "Boss"("ID"),
                    "Stamina" INT,
                    "Strength" INT,
                    "Agility" INT,
                    "Intellect" INT,
                    "Versatility" INT,
                    "Critical_Strike" INT,
                    "Haste" INT,
                    "Mastery" INT,
                    "Spell" TEXT,
                    "Description" TEXT)""")
    conn.commit()
    print("Setup databse complete")


def add_to_database(object_list, object_type):
    '''
    Function to add list of objects to the database table
    @params:
        object_list: a list of objects of type object_type
        object_type: str the type of object
    @return:
        none
    '''

    if object_type == "boss":
        for i in object_list:
            cur.execute(
                """INSERT INTO "Boss"("Name", "ID", "Level", "Level_Heroic", "Level_Heoic_Repr", "Zone", "Description") VALUES(%s, %s, %s, %s, %s, %s, %s) on conflict do nothing""",
                i.toTuple())
        conn.commit()
    elif object_type == "loot":
        for i in object_list:
            cur.execute(
                """INSERT INTO "Loot"("Name", "ID", "Item_Level", "Boss_ID", "Stamina", "Strength", "Agility", "Intellect", "Versatility", "Critical_Strike", "Haste", "Mastery", "Spell", "Description") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing""",
                i.toTuple())
        conn.commit()
    else:
        print("Object type not supported")

# O(1) search
'''
# Update: scraping wowdb.com can make a better O(1) search. Considering swtich to that in future versions.
# since at this point O(n) search turns out to be generally faster than O(1) search, and it is less dangerous to
make repeated requests to Blizzard API than to wowhead.com, I choose to adopt O(n) method at this point of time.

def search(search_term):
    startTime = datetime.now()
    test = BeautifulSoup(
        requests.get(
            "http://www.wowhead.com/" +
            search_term).text,
        "html.parser")
    # print(test)
    ul = test.find_all("tr")

    s = ul[0].find_all("script")
    s = s[0].text

    s = s[s.find("Zone ID") + 9: s.find("[", s.find("Zone ID"))]
    # print(ul)
    print(s)
    i = json.loads(
        requests.get(
            "https://us.api.battle.net/wow/zone/{}?locale=en_US&apikey=9sw5r4nkqxpbsvvysxdcpp8spxu7tejv".format(s)).text)
    print(i)

    timeElapsed = datetime.now() - startTime
    print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))
'''


if __name__ == '__main__':
    command = None
    search_term = []
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if len(sys.argv) > 2:
            for i in range(2, len(sys.argv)):
                search_term.append(sys.argv[i])
            search_term = ("-").join(search_term).lower()

    if command == 'setup':
        print('setting up database')
        setup_database()
    elif command == 'search':
        print('searching', search_term)
        search_zones(search_term)
        # search(search_term)
    elif command == 'clean':
        clean_cache()
        print('Cache has been cleaned.')
    else:
        print('nothing to do')
