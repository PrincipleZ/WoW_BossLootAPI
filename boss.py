class Boss(object):
    self.lootList = []

    def __init__(
            self,
            name,
            id,
            level,
            level_heroic,
            zondID,
            zone,
            description):
        self.name = name
        self.id = id
        self.level = level
        self.level_heroic = level_heroic
        self.zoneID = zoneID
        self.zone = zone
        self.description = description

    def __str__(self):
        return "{0} \n {1}, Level {2}, Heroic Mode Level {3} \n {4}".format(
            self.zone, self.name, self.level, self.level_heroic, self.description)

    def add_loot(self, loot):
        self.lootList.append(loot)

    def toDict(self):
        return {
            "Name": self.name,
            "ID": self.id,
            "Level": self.level,
            "Heroic_Level": self.level_heroic,
            "ZoneID": self.zoneID,
            "Zone": self.zone,
            "Description": self.description
        }
