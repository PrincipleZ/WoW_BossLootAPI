from SI507F17_finalproject import *
import unittest
import os

sample_boss_url = "http://www.wowdb.com/npcs/36597-the-lich-king"
boss_cache_file = "test_boss_data.json"
loot_cache_file = "test_loot_data.json"
sample_boss = {
    "name": "The Lich King",
    "id": 36597,
    "npc": [36597],
    "level": 83,
    "level_heroic": 83,
    "zone_id": 4812,
    "zone": "Icecrown Citadel",
    "description": ""
}
sample_loot = {
    "name": "Royal Scepter of Terenas II",
    "id": 50734,
    "ilevel": 284,
    "boss_id": 36597,
    "stats": [{
            "stat": 32,
            "amount": 2
    }, {
        "stat": 36,
        "amount": 10
    }, {
        "stat": 5,
        "amount": 154
    }, {
        "stat": 7,
        "amount": 22
    }],
    "spell": [],
    "description": "Though broken and corrupt, you can still make out the royal seal of Lordaeron."
}


class PreTest(unittest.TestCase):

    def test_key(self):
        self.assertTrue(API_KEY)

    def test_database(self):
        conn, cur = db_connect_cursor()
        self.assertTrue(conn)
        self.assertTrue(cur)


class TestBoss(unittest.TestCase):

    def setUp(self):
        self.name = sample_boss["name"]
        self.id = sample_boss["id"]
        self.npc = sample_boss["npc"]
        self.level = sample_boss["level"]
        self.level_heroic = sample_boss["level_heroic"]
        self.zone_id = sample_boss["zone_id"]
        self.zone = sample_boss["zone"]
        self.description = sample_boss["description"]
        self.boss = Boss(
            self.name,
            self.id,
            self.npc,
            self.level,
            self.level_heroic,
            self.zone_id,
            self.zone,
            self.description)

    def test_init(self):

        self.assertEqual(self.boss.name, self.name)
        self.assertEqual(self.boss.id, self.id)
        self.assertEqual(self.boss.npc, self.npc)
        self.assertEqual(self.boss.level, self.level)
        self.assertEqual(self.boss.level_heroic, self.level_heroic)
        self.assertEqual(self.boss.zoneID, self.zone_id)
        self.assertEqual(self.boss.zone, self.zone)
        self.assertEqual(self.boss.description, self.description)

    def test_add_loot(self):
        test_loot = Loot("test", 0, 0, 0, [], [], "")
        self.boss.add_loot(test_loot)
        self.assertEqual(len(self.boss.lootList), 1)

    def test_contain(self):
        test_loot = Loot("test", 0, 0, 0, [], [], "")
        self.boss.add_loot(test_loot)
        self.assertTrue("test" in self.boss)

    def test_repr(self):
        self.assertEqual(repr(self.boss), "Boss 36597")

    def test_toDict(self):
        self.assertIsInstance(self.boss.toDict(), dict)


class TestLoot(unittest.TestCase):

    def setUp(self):
        self.name = sample_loot["name"]
        self.id = sample_loot["id"]
        self.ilevel = sample_loot["ilevel"]
        self.boss_id = sample_loot["boss_id"]
        self.stats = sample_loot["stats"]
        self.spell = sample_loot["spell"]
        self.description = sample_loot["description"]
        self.loot = Loot(
            self.name,
            self.id,
            self.ilevel,
            self.boss_id,
            self.stats,
            self.spell,
            self.description)

    def test_init(self):
        self.assertEqual(self.loot.name, self.name)
        self.assertEqual(self.loot.id, self.id)
        self.assertEqual(self.loot.ilevel, self.ilevel)
        self.assertEqual(self.loot.boss_id, self.boss_id)
        self.assertEqual(self.loot.description, self.description)

    def test_parse_stats(self):
        for i in self.loot.stats.keys():
            self.assertIsInstance(i, str)

    def test_stats_to_string(self):
        self.assertIsInstance(self.loot.stats_to_string(), str)


class Test(unittest.TestCase):

    def setUp(self):
        self.conn, self.cur = db_connect_cursor()
        self.test_boss = Boss(
            sample_boss["name"],
            sample_boss["id"],
            sample_boss["npc"],
            sample_boss["level"],
            sample_boss["level_heroic"],
            sample_boss["zone_id"],
            sample_boss["zone"],
            sample_boss["description"])
        # self.test_boss = Boss()

    def test_zone_cache(self):
        sample_data = json.loads(
            requests.get(
                "https://us.api.battle.net/wow/zone/?locale=en_US&apikey={}".format(API_KEY)).text)
        test_data = set_cache("test_cache.json")
        del test_data['time_stamp']
        del test_data['expire_in_days']
        self.assertEqual(sample_data, test_data)
        self.assertTrue(os.path.isfile("test_cache.json"))

    def test_boss_cache(self):
        test_data = load_boss_cache(sample_boss_url, boss_cache_file)
        self.assertTrue(os.path.isfile(boss_cache_file))

    def test_search_loot(self):
        self.loot_list = search_loot(self.test_boss)
        self.assertIsInstance(self.loot_list, list)
        self.assertTrue(len(self.loot_list) > 1)
        for i in self.loot_list:
            self.assertIsInstance(i, Loot)

    def test_boss_add_to_database(self):
        setup_database()
        add_to_database([self.test_boss], "boss")
        self.cur.execute(
            """SELECT * FROM "Boss" WHERE "Name" LIKE '%Lich%' """)
        result = self.cur.fetchall()
        self.assertTrue(len(result), 1)
        self.assertEqual(result[0]["Name"], sample_boss['name'])
        self.assertEqual(result[0]["ID"], sample_boss['id'])

    def test_loot_add_to_database(self):
        setup_database()
        self.loot_list = search_loot(self.test_boss)
        add_to_database(self.loot_list, "loot")
        self.cur.execute(
            """SELECT * FROM "Loot" WHERE "Boss_ID" = '36597' """)
        result = self.cur.fetchall()
        self.assertEqual(len(result), len(self.loot_list))


if __name__ == "__main__":
    unittest.main(verbosity=2)
