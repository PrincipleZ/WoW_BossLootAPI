from stat_dict import stat_dict


class Loot(object):

    def __init__(self, name, id, ilevel, boss_id, stats, spell, description):
        self.name = name
        self.id = id
        self.ilevel = ilevel
        self.boss_id = boss_id
        self.stats = self.parse_stats(stats)
        self.spell = self.parse_spell(spell)
        self.description = description

    def __str__(self):
        return "{0}\niLevel: {1}\n{2}\n{3}".format(
            self.name, self.ilevel, self.stats_to_string(), self.spell)

    def toDict(self):
        basedict = {
            "Name": self.name,
            "ID": self.id,
            "Item_Level": self.ilevel,
            "Boss_ID": self.boss_id,
            "Spell": self.spell,
            "Description": self.description
        }
        basedict.update(self.stats)
        return basedict

    def parse_stats(self, stats):
        newdict = {"Stamina": 0,
                   "Strength": 0,
                   "Agility": 0,
                   "Intellect": 0,
                   "Versatility": 0,
                   "Critical_Strike": 0,
                   "Haste": 0,
                   "Mastery": 0
                   }
        if stats:
            for i in stats:
                k = i['stat']
                v = i['amount']
                if k == 71:
                    newdict['Strength'] = v
                    newdict['Agility'] = v
                    newdict['Intellect'] = v
                elif k == 73:
                    newdict['Agility'] = v
                    newdict['Intellect'] = v
                elif k == 74:
                    newdict['Strength'] = v
                    newdict['Intellect'] = v
                elif k in stat_dict:
                    newdict[stat_dict[k]] = v
        return newdict

    def stats_to_string(self):
        res = ""
        for k, v in self.stats:
            if v != 0:
                temp = k + ": " + str(v) + "\n"
                res += temp
        return res

    def parse_spell(self, spell):
        spell_list = []
        for i in spell:
            if "spell" not in i:
                pass
            else:
                if i['spell']['castTime'] == "Passive":
                    spell_list.append("Equip: " + i['spell']['description'])
                else:
                    cooldown = ""
                    try:
                        cooldown = i['spell']['cooldown']
                    except:
                        cooldown = "0s"
                    spell_list.append(
                        "Use: {0} ({1})".format(
                            i['spell']['description'],
                            cooldown))
        return "\n".join(spell_list)

    def toTuple(self):
        tempdict = self.toDict()
        return (tempdict["Name"],
                tempdict["ID"],
                tempdict["Item_Level"],
                tempdict["Boss_ID"],
                tempdict["Stamina"],
                tempdict["Strength"],
                tempdict["Agility"],
                tempdict["Intellect"],
                tempdict["Versatility"],
                tempdict["Critical_Strike"],
                tempdict["Haste"],
                tempdict["Mastery"],
                tempdict["Spell"],
                tempdict["Description"]
                )
