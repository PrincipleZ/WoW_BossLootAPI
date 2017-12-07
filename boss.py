class Boss(object):

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
        self.heroic_level_repr = level_heroic
        if (level_heroic == 0):
            self.heroic_level_repr = "N/A"
        self.zoneID = zoneID
        self.zone = zone
        self.description = description
        self.lootList = []

    def __str__(self):
        return "{0} \n {1}, Level {2}, Heroic Mode Level {3} \n {4}".format(
            self.zone, self.name, self.level, self.level_heroic_repr, self.description)

    def __repr__(self):
        return "Boss {0}".format(self.id)

    def __contains__(self, loot):
        lst = []
        for i in self.lootList:
            lst.append(i.name)
            lst.append(i.id)
            if loot == i:
                return True
        return loot in lst

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
