import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup

# functions borrowed from project 5 to set timestamp to cache and check if
# the cache is outdated


def write_time_stamp(input, expire_in_days):
    '''
    Function to write time stamp and expiration time
    @params:
        input: data in dictionary
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
        input: data in dictionary
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
        filename: filename of the cache file
    @return:
        data in json dictionary
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
        set_cache(filename)


def set_cache(filename):
    '''
    Function to request data of all the zones and save in cachefile
    @param: filename of the cache file
    @return: data in json dictionary
    '''
    data = json.loads(requests.get(
        "https://us.api.battle.net/wow/zone/?locale=en_US&apikey=9sw5r4nkqxpbsvvysxdcpp8spxu7tejv").text)
    write_time_stamp(data, 2)
    with open(filename, 'w') as f:
        f.write(json.dumps(data))
    return data

# O(n) search


def search_zones(search_term):
    '''
    Search the zone based on input on wowhead
    Search flow: Get zones info from zones list, get bosses info from zones info,
                 get item list from wowhead using bosses info, get item info from Blizzard API
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
    print(res)
    # timeElapsed = datetime.now() - startTime
    # print('Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))


# O(1) search
'''
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
