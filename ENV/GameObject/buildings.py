from typing import List
from .config import *

class BaseBuilding:
    TYPE_EMPTY      = 0x00
    TYPE_DEFENSE    = 0x01
    TYPE_RESOURCE   = 0x02
    TYPE_WALL       = 0x03
    TYPE_TOWNHALL   = 0x04
    TYPE_OTHERS     = 0x05

    IMG_MAP = {
        'TownHall':     "images/buildings/town_hall",
        'ClanCastle':   "images/buildings/clan_castle",
        'Wall':         "images/buildings/wall",
        'ArmyCamp':     "images/buildings/army_camp",
        'Barrack':      "images/buildings/barracks",
        'Laboratory':   "images/buildings/laboratory",
        'SpellForge':   "images/buildings/spell_factory",
        'BuilderHut':   "images/buildings/builder's_hut",
        'ElixirPump':   "images/buildings/elixir_collector",
        'GoldMine':     "images/buildings/gold_mine",
        'ElixirStorage':"images/buildings/elixir_storage",
        'GoldStorage':  "images/buildings/gold_storage",
        'Cannon':       "images/buildings/cannon",
        'ArcherTower':  "images/buildings/archer_tower",
        'Mortar':       "images/buildings/mortar",
        'AirDefense':   "images/buildings/air_defense",
        'WizardTower':  "images/buildings/wizard_tower",
    }

    ID_MAP = {
        'TownHall':     0,
        'ClanCastle':   1,
        'Wall':         2,
        'ArmyCamp':     3,
        'Barrack':      4,
        'Laboratory':   5,
        'SpellForge':   6,
        'BuilderHut':   7,
        'ElixirPump':   8,
        'GoldMine':     9,
        'ElixirStorage':10,
        'GoldStorage':  11,
        'Cannon':       12,
        'ArcherTower':  13,
        'Mortar':       14,
        'AirDefense':   15,
        'WizardTower':  16,
    }

    ID_NAME_MAP = {
        0: 'TownHall',
        1: 'ClanCastle',
        2: 'Wall',
        3: 'ArmyCamp',
        4: 'Barrack',
        5: 'Laboratory',
        6: 'SpellForge',
        7: 'BuilderHut',
        8: 'ElixirPump',
        9: 'GoldMine',
        10: 'ElixirStorage',
        11: 'GoldStorage',
        12: 'Cannon',
        13: 'ArcherTower',
        14: 'Mortar',
        15: 'AirDefense',
        16: 'WizardTower'
    }

    def __init__(self, name, level):
        self.id = BaseBuilding.getID(name)
        assert(self.id != -1)
        self.name = name
        self.level = level
        self.type = BaseBuilding.TYPE_OTHERS
        self.hp = 0
        self.remHp = 0
        self.height = 0
        self.width = 0

    def getWidth(self) -> int:
        return self.width
    
    @staticmethod
    def getID(name: str) -> int:
        if name not in BaseBuilding.ID_MAP:
            return -1
        return BaseBuilding.ID_MAP[name]
    
    def getHeight(self) -> int:
        return self.height
    
    def getHp(self) -> int:
        return self.hp
    
    def getRemHp(self) -> int:
        return self.remHp
    
    def getHealthPercentage(self) -> float:
        return self.remHp * 100.0 / self.hp if self.hp > 0 else 0.0
    
    def getImagePath(self) -> str:
        return BaseBuilding.IMG_MAP.get(self.name, None) + f"/level_{self.level}.png"
    
    def __str__(self):
        return f"{self.name} (Level {self.level}) with {self.hp} HP"

class TownHallBuilding(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 450,
            'capacity': 1000,
        },
        # Level 2
        2: {
            'hp': 1600,
            'capacity': 2500,
        },
        # Level 3
        3: {
            'hp': 1850,
            'capacity': 10000,
        },
        # Level 4
        4: {
            'hp': 2100,
            'capacity': 50000,
        },
        # Level 5
        5: {
            'hp': 2400,
            'capacity': 100000,
        },

    }

    def __init__(self, level):
        assert(1 <= level <= 5)
        super().__init__("TownHall", level)
        self.type = BaseBuilding.TYPE_TOWNHALL
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 4
        self.width = 4
        self.capacity = self.ATTR_MAP[level]['capacity']
        self.elixir = self.capacity
        self.gold = self.capacity

class DefenseBuilding(BaseBuilding):
    def __init__(self, name, level):
        super().__init__(name, level)
        self.type = BaseBuilding.TYPE_DEFENSE
        self.hp = 0
        self.remHp = 0
        self.height = 0
        self.width = 0
        self.atkSpeed = 0
        self.dph = 0
        self.airTarget = False
        self.grndTarget = False
        self.minRange = 0
        self.maxRange = 0
        self.damageRadius = 0

    def getAtkSpeed(self) -> int:
        return self.atkSpeed
    
    def getDph(self) -> int:
        return self.dph
    
    def attackAir(self) -> bool:
        return self.airTarget
    
    def attackGround(self) -> bool:
        return self.grndTarget
    
    def getMinRange(self) -> int:
        return self.minRange
    
    def getMaxRange(self) -> int:
        return self.maxRange
    
    def getTargetDomain(self) -> int:
        return (self.attackAir() << 1) + self.attackGround()

    
class ResourceBuilding(BaseBuilding):
    def __init__(self, name, level):
        super().__init__(name, level)
        self.type = BaseBuilding.TYPE_RESOURCE
        self.hp = 0
        self.remHp = 0
        self.height = 0
        self.width = 0
        self.capacity = 0
        self.gold = 0
        self.elixir = 0

    def getCapacity(self) -> int:
        return self.capacity
    
    def getGold(self) -> int:
        return self.gold
    
    def getElixir(self) -> int:
        return self.elixir
    
class WallBuilding(BaseBuilding):

    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 300,
        },
        # Level 2
        2: {
            'hp': 500,
        },
        # Level 3
        3: {
            'hp': 700,
        },
        # Level 4
        4: {
            'hp': 900,
        },
        # Level 5
        5: {
            'hp': 1400,
        },
    }

    def __init__(self, level=1):
        super().__init__("Wall", level)
        self.type = BaseBuilding.TYPE_WALL
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 1
        self.width = 1

class Cannon(DefenseBuilding):

    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 420,
            'dps': 9,
        },
        # Level 2
        2: {
            'hp': 470,
            'dps': 11,
        },
        # Level 3
        3: {
            'hp': 520,
            'dps': 15,
        },
        # Level 4
        4: {
            'hp': 570,
            'dps': 19,
        },
        # Level 5
        5: {
            'hp': 620,
            'dps': 25,
        },
        6: {
            'hp': 670,
            'dps': 31,
        }
    }

    def __init__(self, level=1):
        super().__init__('Cannon', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.atkSpeed = int(800/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 1e+3
        self.airTarget = False
        self.grndTarget = True
        self.height = 3
        self.width = 3
        self.minRange = 0
        self.maxRange = 9

class ArcherTower(DefenseBuilding):
    
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 380,
            'dps': 11,
        },
        # Level 2
        2: {
            'hp': 420,
            'dps': 15,
        },
        # Level 3
        3: {
            'hp': 460,
            'dps': 19,
        },
        # Level 4
        4: {
            'hp': 500,
            'dps': 25,
        },
        # Level 5
        5: {
            'hp': 540,
            'dps': 30,
        },
        6: {
            'hp': 580,
            'dps': 35,

        }
    }

    def __init__(self, level=1):
        super().__init__('ArcherTower', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.atkSpeed = int(500/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 1e+3
        self.airTarget = True
        self.grndTarget = True
        self.height = 3
        self.width = 3
        self.minRange = 0
        self.maxRange = 10

class Mortar(DefenseBuilding):
        
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 400,
            'dps': 4,
        },
        # Level 2
        2: {
            'hp': 450,
            'dps': 5,
        },
        # Level 3
        3: {
            'hp': 500,
            'dps': 6,
        },
        # Level 4
        4: {
            'hp': 550,
            'dps': 7,
        },
        # Level 5
        5: {
            'hp': 600,
            'dps': 9,
        },
    }

    def __init__(self, level=1):
        super().__init__('Mortar', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.atkSpeed = int(5000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]['dps'] * self.atkSpeed * MILISECONDS_PER_FRAME / 1e+3
        self.airTarget = False
        self.grndTarget = True
        self.height = 3
        self.width = 3
        self.minRange = 4
        self.maxRange = 11
        self.damageRadius = 1

class AirDefense(DefenseBuilding):

    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 800,
            'dps': 80,
        },
        # Level 2
        2: {
            'hp': 850,
            'dps': 110,
        },
        # Level 3
        3: {
            'hp': 900,
            'dps': 140,
        },
        # Level 4
        4: {
            'hp': 950,
            'dps': 160,
        },
        # Level 5
        5: {
            'hp': 1000,
            'dps': 190,
        },
    }

    def __init__(self, level=1):
        super().__init__('AirDefense', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.atkSpeed = int(1000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 1e+3
        self.airTarget = True
        self.grndTarget = False
        self.height = 3
        self.width = 3
        self.minRange = 0
        self.maxRange = 10

class WizardTower(DefenseBuilding):

    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 620,
            'dps': 11,
        },
        # Level 2
        2: {
            'hp': 650,
            'dps': 13,
        },
        # Level 3
        3: {
            'hp': 680,
            'dps': 16,
        },
        # Level 4
        4: {
            'hp': 730,
            'dps': 20,
        },
        # Level 5
        5: {
            'hp': 840,
            'dps': 24,
        },
    }

    def __init__(self, level=1):
        super().__init__('WizardTower', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.atkSpeed = int(1700/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 1e+3
        self.airTarget = True
        self.grndTarget = True
        self.height = 3
        self.width = 3
        self.minRange = 0
        self.maxRange = 7
        self.damageRadius = 1

class GoldMine(ResourceBuilding):
        
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 400,
            'capacity': 1000,
            'gold': 200,
        },
        # Level 2
        2: {
            'hp': 440,
            'capacity': 2000,
            'gold': 400,
        },
        # Level 3
        3: {
            'hp': 480,
            'capacity': 3000,
            'gold': 600,
        },
        # Level 4
        4: {
            'hp': 520,
            'capacity': 5000,
            'gold': 800,
        },
        # Level 5
        5: {
            'hp': 560,
            'capacity': 10000,
            'gold': 1000,
        },
        6: {
            'hp': 600,
            'capacity': 20000,
            'gold': 1300,
        },
        7: {
            'hp': 640,
            'capacity': 30000,
            'gold': 1600,
        },
        8: {
            'hp': 680,
            'capacity': 50000,
            'gold': 1900,
        },
        9: {
            'hp': 720,
            'capacity': 75000,
            'gold': 2200,
        },
        10: {
            'hp': 780,
            'capacity': 100000,
            'gold': 2800,
        },
    }

    def __init__(self, level=1):
        super().__init__('GoldMine', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.capacity = self.ATTR_MAP[level]['capacity']
        self.gold = self.ATTR_MAP[level]['gold']
        self.elixir = 0
        self.height = 3
        self.width = 3     

class ElixirPump(ResourceBuilding):
        
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 400,
            'capacity': 1000,
            'elixir': 200,
        },
        # Level 2
        2: {
            'hp': 440,
            'capacity': 2000,
            'elixir': 400,
        },
        # Level 3
        3: {
            'hp': 480,
            'capacity': 3000,
            'elixir': 600,
        },
        # Level 4
        4: {
            'hp': 520,
            'capacity': 5000,
            'elixir': 800,
        },
        # Level 5
        5: {
            'hp': 560,
            'capacity': 10000,
            'elixir': 1000,
        },
        6: {
            'hp': 600,
            'capacity': 20000,
            'elixir': 1300,
        },
        7: {
            'hp': 640,
            'capacity': 30000,
            'elixir': 1600,
        },
        8: {
            'hp': 680,
            'capacity': 50000,
            'elixir': 1900,
        },
        9: {
            'hp': 720,
            'capacity': 75000,
            'elixir': 2200,
        },
        10: {
            'hp': 780,
            'capacity': 100000,
            'elixir': 2800,
        },
    }

    def __init__(self, level=1):
        super().__init__('ElixirPump', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.capacity = self.ATTR_MAP[level]['capacity']
        self.gold = 0
        self.elixir = self.ATTR_MAP[level]['elixir']
        self.height = 3
        self.width = 3 

class GoldStorage(ResourceBuilding):
            
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 400,
            'capacity': 1500,
        },
        # Level 2
        2: {
            'hp': 600,
            'capacity': 3000,
        },
        # Level 3
        3: {
            'hp': 800,
            'capacity': 6000,
        },
        # Level 4
        4: {
            'hp': 1000,
            'capacity': 12000,
        },
        # Level 5
        5: {
            'hp': 1200,
            'capacity': 25000,
        },
        6: {
            'hp': 1400,
            'capacity': 45000,
        },
        7: {
            'hp': 1600,
            'capacity': 100000,
        },
        8: {
            'hp': 1700,
            'capacity': 225000,
        },
        9: {
            'hp': 1800,
            'capacity': 450000,
        },
        10: {
            'hp': 1900,
            'capacity': 850000,
        },
    }

    def __init__(self, level=1):
        super().__init__('GoldStorage', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.capacity = self.ATTR_MAP[level]['capacity']
        self.gold = self.capacity
        self.elixir = 0
        self.height = 3
        self.width = 3

class ElixirStorage(ResourceBuilding):              
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 400,
            'capacity': 1500,
        },
        # Level 2
        2: {
            'hp': 600,
            'capacity': 3000,
        },
        # Level 3
        3: {
            'hp': 800,
            'capacity': 6000,
        },
        # Level 4
        4: {
            'hp': 1000,
            'capacity': 12000,
        },
        # Level 5
        5: {
            'hp': 1200,
            'capacity': 25000,
        },
        6: {
            'hp': 1400,
            'capacity': 45000,
        },
        7: {
            'hp': 1600,
            'capacity': 100000,
        },
        8: {
            'hp': 1700,
            'capacity': 225000,
        },
        9: {
            'hp': 1800,
            'capacity': 450000,
        },
        10: {
            'hp': 1900,
            'capacity': 850000,
        },
    }

    def __init__(self, level=1):
        super().__init__('ElixirStorage', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.capacity = self.ATTR_MAP[level]['capacity']
        self.gold = 0
        self.elixir = self.capacity
        self.height = 3
        self.width = 3

class ArmyCamp(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 250,
        },
        # Level 2
        2: {
            'hp': 270,
        },
        # Level 3
        3: {
            'hp': 290,
        },
        # Level 4
        4: {
            'hp': 310,
        },
        # Level 5
        5: {
            'hp': 330,
        },
    }

    def __init__(self, level=1):
        super().__init__('ArmyCamp', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 4
        self.width = 4

class Barrack(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 250,
        },
        # Level 2
        2: {
            'hp': 290,
        },
        # Level 3
        3: {
            'hp': 330,
        },
        # Level 4
        4: {
            'hp': 370,
        },
        # Level 5
        5: {
            'hp': 420,
        },
        6: {
            'hp': 470,
        },
        7: {
            'hp': 520,
        },
    }

    def __init__(self, level=1):
        super().__init__('Barrack', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 3
        self.width = 3

class Laboratory(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 500,
        },
        # Level 2
        2: {
            'hp': 550,
        },
        # Level 3
        3: {
            'hp': 600,
        },
        # Level 4
        4: {
            'hp': 650,
        },
        # Level 5
        5: {
            'hp': 700,
        },
    }

    def __init__(self, level=1):
        super().__init__('Laboratory', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 3
        self.width = 3

class SpellForge(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 500,
        },
        # Level 2
        2: {
            'hp': 550,
        },
        # Level 3
        3: {
            'hp': 600,
        },
        # Level 4
        4: {
            'hp': 650,
        },
        # Level 5
        5: {
            'hp': 700,
        },
    }

    def __init__(self, level=1):
        super().__init__('SpellForge', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 3
        self.width = 3

class BuilderHut(BaseBuilding):
    def __init__(self, level=1):
        super().__init__('BuilderHut', level)
        self.hp = 250
        self.remHp = self.hp
        self.height = 2
        self.width = 2

class ClanCastle(BaseBuilding):
    ATTR_MAP = {
        # Level 1
        1: {
            'hp': 1000,
        },
        # Level 2
        2: {
            'hp': 1400,
        },
        # Level 3
        3: {
            'hp': 2000,
        },
        # Level 4
        4: {
            'hp': 2600,
        },
        # Level 5
        5: {
            'hp': 3000,
        },
    }

    def __init__(self, level=1):
        super().__init__('ClanCastle', level)
        self.hp = self.ATTR_MAP[level]['hp']
        self.remHp = self.hp
        self.height = 3
        self.width = 3

class BuildingDirectory:

    BUILDING_MAP = {
        'TownHall':     TownHallBuilding,
        'ClanCastle':   ClanCastle,
        'Wall':         WallBuilding,
        'ArmyCamp':     ArmyCamp,
        'Barrack':      Barrack,
        'Laboratory':   Laboratory,
        'SpellForge':   SpellForge,
        'BuilderHut':   BuilderHut,
        'ElixirPump':   ElixirPump,
        'GoldMine':     GoldMine,
        'ElixirStorage':ElixirStorage,
        'GoldStorage':  GoldStorage,
        'Cannon':       Cannon,
        'ArcherTower':  ArcherTower,
        'Mortar':       Mortar,
        'AirDefense':   AirDefense,
        'WizardTower':  WizardTower,
    }
    
    BUILDING_LEVEL_MAP = {
        # Townhall 1
        1: {
            'TownHall': 1,
            'ClanCastle': 0,
            'Wall': 0,
            'ArmyCamp': 1,
            'Barrack': 1,
            'Laboratory': 0,
            'SpellForge': 0,
            'BuilderHut': 1,
            'ElixirPump': 1,
            'GoldMine': 1,
            'ElixirStorage': 1,
            'GoldStorage': 1,
            'Cannon': 1,
            'ArcherTower': 0,
            'Mortar': 0,
            'AirDefense': 0,
            'WizardTower': 0,
        },
        # Townhall 2
        2: {
            'TownHall': 2,
            'ClanCastle': 0,
            'Wall': 2,
            'ArmyCamp': 2,
            'Barrack': 4,
            'Laboratory': 0,
            'SpellForge': 0,
            'BuilderHut': 1,
            'ElixirPump': 4,
            'GoldMine': 4,
            'ElixirStorage': 3,
            'GoldStorage': 3,
            'Cannon': 3,
            'ArcherTower': 2,
            'Mortar': 0,
            'AirDefense': 0,
            'WizardTower': 0,
        },
        # Townhall 3
        3: {
            'TownHall': 3,
            'ClanCastle': 1,
            'Wall': 3,
            'ArmyCamp': 3,
            'Barrack': 5,
            'Laboratory': 1,
            'SpellForge': 0,
            'BuilderHut': 1,
            'ElixirPump': 6,
            'GoldMine': 6,
            'ElixirStorage': 6,
            'GoldStorage': 6,
            'Cannon': 4,
            'ArcherTower': 3,
            'Mortar': 1,
            'AirDefense': 0,
            'WizardTower': 0,
        },
        # Townhall 4
        4: {
            'TownHall': 4,
            'ClanCastle': 2,
            'Wall': 4,
            'ArmyCamp': 4,
            'Barrack': 6,
            'Laboratory': 2,
            'SpellForge': 0,
            'BuilderHut': 1,
            'ElixirPump': 8,
            'GoldMine': 8,
            'ElixirStorage': 8,
            'GoldStorage': 8,
            'Cannon': 5,
            'ArcherTower': 4,
            'Mortar': 2,
            'AirDefense': 2,
            'WizardTower': 0,
        },
        # Townhall 5
        5: {
            'TownHall': 5,
            'ClanCastle': 2,
            'Wall': 5,
            'ArmyCamp': 5,
            'Barrack': 7,
            'Laboratory': 3,
            'SpellForge': 1,
            'BuilderHut': 1,
            'ElixirPump': 10,
            'GoldMine': 10,
            'ElixirStorage': 9,
            'GoldStorage': 9,
            'Cannon': 6,
            'ArcherTower': 6,
            'Mortar': 3,
            'AirDefense': 3,
            'WizardTower': 2,
        },
    }
    BUILDING_MAX_COUNT_MAP = {
        # Townhall 1
        1: {
            'TownHall': 1,
            'ClanCastle': 0,
            'Wall': 0,
            'ArmyCamp': 1,
            'Barrack': 1,
            'Laboratory': 0,
            'SpellForge': 0,
            'BuilderHut': 5,
            'ElixirPump': 1,
            'GoldMine': 1,
            'ElixirStorage': 1,
            'GoldStorage': 1,
            'Cannon': 1,
            'ArcherTower': 0,
            'Mortar': 0,
            'AirDefense': 0,
            'WizardTower': 0,
        },
        # Townhall 2
        2: {
            'TownHall': 1,
            'ClanCastle': 0,
            'Wall': 25,
            'ArmyCamp': 1,
            'Barrack': 1,
            'Laboratory': 0,
            'SpellForge': 0,
            'BuilderHut': 5,
            'ElixirPump': 2,
            'GoldMine': 2,
            'ElixirStorage': 1,
            'GoldStorage': 1,
            'Cannon': 2,
            'ArcherTower': 1,
            'Mortar': 0,
            'AirDefense': 0,
            'WizardTower': 0
        },
        # Townhall 3
        3: {
            'TownHall': 1,
            'ClanCastle': 1,
            'Wall': 50,
            'ArmyCamp': 1,
            'Barrack': 2,
            'Laboratory': 1,
            'SpellForge': 0,
            'BuilderHut': 5,
            'ElixirPump': 3,
            'GoldMine': 3,
            'ElixirStorage': 2,
            'GoldStorage': 2,
            'Cannon': 2,
            'ArcherTower': 1,
            'Mortar': 1,
            'AirDefense': 0,
            'WizardTower': 0
        },
        # Townhall 4
        4: {
            'TownHall': 1,
            'ClanCastle': 1,
            'Wall': 75,
            'ArmyCamp': 1,
            'Barrack': 2,
            'Laboratory': 1,
            'SpellForge': 0,
            'BuilderHut': 5,
            'ElixirPump': 4,
            'GoldMine': 4,
            'ElixirStorage': 2,
            'GoldStorage': 2,
            'Cannon': 2,
            'ArcherTower': 2,
            'Mortar': 1,
            'AirDefense': 1,
            'WizardTower': 0
        },
        # Townhall 5
        5: {
            'TownHall': 1,
            'ClanCastle': 1,
            'Wall': 100,
            'ArmyCamp': 1,
            'Barrack': 1,
            'Laboratory': 1,
            'SpellForge': 1,
            'BuilderHut': 5,
            'ElixirPump': 5,
            'GoldMine': 5,
            'ElixirStorage': 2,
            'GoldStorage': 2,
            'Cannon': 3,
            'ArcherTower': 3,
            'Mortar': 1,
            'AirDefense': 1,
            'WizardTower': 1
        },
    }

    def __init__(self, townHallLevel: int):
        self.townHallLevel = townHallLevel
        self.buildings = {}
        self.populateBuildings()


    def populateBuildings(self):
        for name, level in BuildingDirectory.BUILDING_LEVEL_MAP[self.townHallLevel].items():
            self.buildings[name] = BuildingDirectory.BUILDING_MAP[name]
    
    def getAllBuildingNames(self) -> List[str]:
        return list(self.buildings.keys())
    
    def getBuildingLevel(self, name: str) -> int:
        return BuildingDirectory.BUILDING_LEVEL_MAP[self.townHallLevel][name]

    def getBuildingObject(self, name: str) -> BaseBuilding:
        return self.buildings[name](self.getBuildingLevel(name))
    
    @staticmethod
    def getBuildingObjectFromID(objID: int, level: int) -> BaseBuilding:
        name = BaseBuilding.ID_NAME_MAP[objID]
        return BuildingDirectory.BUILDING_MAP[name](level)

    def getAll(self) -> List[BaseBuilding]:
        return [self.getBuilding(name) for name in self.buildings]
    
    def getBuildingMaxCount(self, name) -> int:
        return self.BUILDING_MAX_COUNT_MAP[self.townHallLevel][name]

    def __str__(self):
        return f"Building Directory for TownHall Level {self.townHallLevel}\n" + "".join([str(b) + '\n' for b in self.getAll()])
