from stat_dict import stat_dict


class Loot(object):

    def __init__(self, name, id, ilevel, boss_id, stats, spell):
        self.name = name
        self.id = id
        self.ilevel = ilevel
        self.boss_id = boss_id
        self.stats = stats
        self.spell = parse_spell(spell)

    def __str__(self):
        return "{0}\niLevel: {1}\n{2}\n{3}".format(
            self.name, self.ilevel, self.stats_to_string(), self.spell)

    def toDict(self):
        return {
            "Name": self.name,
            "ID": self.id,
            "iLevel": self.ilevel,
            "Boss_ID": self.boss_id,
            "Stats": self.parse_stats(),
            "Spell": self.spell
        }

    def parse_stats(self):
        pass

    def stats_to_string(self):
        pass

    def parse_spell(self, spell):
        pass
