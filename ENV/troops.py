from typing import List
from buildings import BaseBuilding
from config import *

class TroopBase:

    PREFER_DEFENSE  = 0x01
    PREFER_RESOURCE = 0x02
    PREFER_WALL     = 0x03
    PREFER_GENERAL  = 0x04

    ID_MAP = {
        "Barbarian": 1,
        "Archer": 2,
        "Giant": 3,
        "Goblin": 4,
        "Wall Breaker": 5,
        "Balloon": 6,
        "Wizard": 7,
    }

    ID_MAPS_NAME = {
        1: "Barbarian",
        2: "Archer",
        3: "Giant",
        4: "Goblin",
        5: "Wall Breaker",
        6: "Balloon",
        7: "Wizard",
    }

    IMG_MAP = {
        "Barbarian": "images/troops/barbarian.png",
        "Archer": "images/troops/archer.png",
        "Giant": "images/troops/giant.png",
        "Goblin": "images/troops/goblin.png",
        "Wall Breaker": "images/troops/wall_breaker.png",
        "Balloon": "images/troops/balloon.png",
        "Wizard": "images/troops/wizard.png",
    }

    def __init__(self, name, level):
        self.id = TroopBase.genID(name)
        assert(self.id != -1)
        self.name = name
        self.level = level
        self.preference = self.PREFER_GENERAL
        self.hp = 0
        self.remHp = 0
        self.dph = 0
        self.atkRange = 0
        self.atkSpeed = 0
        self.movSpeed = 0
        self.airTarget = False
        self.grndTarget = False
        self.isFlying = False

    @staticmethod
    def genID(name: str) -> int:
        if name not in TroopBase.ID_MAP:
            return -1
        return TroopBase.ID_MAP[name]
    
    def canFly(self) -> bool:
        return self.isFlying
    
    def getAtkRange(self) -> int:
        return self.atkRange
    
    def getAtkSpeed(self) -> int:
        return self.atkSpeed
    
    def getMovSpeed(self) -> int:
        return self.movSpeed
    
    def getHP(self) -> int:
        return self.hp
    
    def getRemHP(self) -> int:
        return self.remHp
    
    def getDph(self) -> int:
        return self.dph
    
    def getPreference(self) -> int:
        return self.preference
    
    def getID(self) -> int:
        return self.troopID
    
    def getHealthPercentage(self) -> float:
        return self.remHp * 100.0 / self.hp if self.hp > 0 else 0.0
    
    def attackAir(self) -> bool:
        return self.airTarget
    
    def attackGround(self) -> bool:
        return self.grndTarget

    def getTargetDomain(self) -> int:
        """
        Target Domain: (01): Ground | (10): Air | (11): Both
        """
        return (int(self.airTarget) << 1) | int(self.grndTarget)

    def getImagePath(self) -> str:
        return self.IMG_MAP[self.name]
    
    def __str__(self):
        return f"{self.name} (Level {self.level}) - HP: {self.hp}, DPS: {self.dph}, Atk Range: {self.atkRange}, Atk Speed: {self.atkSpeed}, Mov Speed: {self.movSpeed}, Air Target: {self.airTarget}, Ground Target: {self.grndTarget}, Flying: {self.isFlying}"

class Barbarian(TroopBase):

    ATTR_MAP = {
        1: {
            "hp": 45,
            "dps": 8,
        },
        2: {
            "hp": 54,
            "dps": 11,
        },
        3: {
            "hp": 65,
            "dps": 14,
        },
        4: {
            "hp": 85,
            "dps": 18,
        },
        5: {
            "hp": 105,
            "dps": 23,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Barbarian", level)
        self.hp = self.ATTR_MAP[level]["hp"]
        self.remHp = self.hp
        self.atkSpeed = int(1000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 0.4
        self.movSpeed = 2 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = False
        self.grndTarget = True
        self.isFlying = False

class Archer(TroopBase):

    ATTR_MAP = {
        1: {
            "hp": 20,
            "dps": 7,
        },
        2: {
            "hp": 23,
            "dps": 9,
        },
        3: {
            "hp": 28,
            "dps": 12,
        },
        4: {
            "hp": 33,
            "dps": 16,
        },
        5: {
            "hp": 40,
            "dps": 20,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Archer", level)
        self.hp = self.ATTR_MAP[level]["hp"]
        self.preference = self.PREFER_GENERAL
        self.remHp = self.hp
        self.atkSpeed = int(1000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 3.5
        self.movSpeed = 3 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = True
        self.grndTarget = True
        self.isFlying = False

class Giant(TroopBase):
        ATTR_MAP = {
            1: {
                "hp": 300,
                "dps": 11,
            },
            2: {
                "hp": 360,
                "dps": 14,
            },
            3: {
                "hp": 450,
                "dps": 19,
            },
            4: {
                "hp": 600,
                "dps": 24,
            },
            5: {
                "hp": 800,
                "dps": 31,
            },
        }
    
        def __init__(self, level):
    
            assert(1 <= level <= 5)
            
            super().__init__("Giant", level)
            self.preference = self.PREFER_DEFENSE
            self.hp = self.ATTR_MAP[level]["hp"]
            self.remHp = self.hp
            self.atkSpeed = int(2000/MILISECONDS_PER_FRAME)
            self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
            self.atkRange = 0.1
            self.movSpeed = 1.5 * MILISECONDS_PER_FRAME / 1000
            self.airTarget = False
            self.grndTarget = True
            self.isFlying = False

class Goblin(TroopBase):
    ATTR_MAP = {
        1: {
            "hp": 25,
            "dps": 11,
        },
        2: {
            "hp": 30,
            "dps": 14,
        },
        3: {
            "hp": 36,
            "dps": 19,
        },
        4: {
            "hp": 50,
            "dps": 24,
        },
        5: {
            "hp": 65,
            "dps": 32,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Goblin", level)
        self.preference = self.PREFER_RESOURCE
        self.hp = self.ATTR_MAP[level]["hp"]
        self.remHp = self.hp
        self.atkSpeed = int(1000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 0.4
        self.movSpeed = 4 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = False
        self.grndTarget = True
        self.isFlying = False

class WallBreaker(TroopBase):
    ATTR_MAP = {
        1: {
            "hp": 20,
            "dps": 6,
        },
        2: {
            "hp": 24,
            "dps": 10,
        },
        3: {
            "hp": 29,
            "dps": 15,
        },
        4: {
            "hp": 35,
            "dps": 20,
        },
        5: {
            "hp": 53,
            "dps": 43,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Wall Breaker", level)
        self.preference = self.PREFER_WALL
        self.hp = self.ATTR_MAP[level]["hp"]
        self.remHp = self.hp
        self.atkSpeed = int(1000/MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 0.5
        self.movSpeed = 3 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = False
        self.grndTarget = True
        self.isFlying = False

class Balloon(TroopBase):
    ATTR_MAP = {
        1: {
            "hp": 150,
            "dps": 25,
        },
        2: {
            "hp": 180,
            "dps": 32,
        },
        3: {
            "hp": 216,
            "dps": 48,
        },
        4: {
            "hp": 280,
            "dps": 72,
        },
        5: {
            "hp": 390,
            "dps": 108,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Balloon", level)
        self.preference = self.PREFER_DEFENSE
        self.hp = self.ATTR_MAP[level]["hp"]
        self.remHp = self.hp
        self.atkSpeed = int(3000 / MILISECONDS_PER_FRAME)
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 0
        self.movSpeed = 1.3 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = False
        self.grndTarget = True
        self.isFlying = True

class Wizard(TroopBase):
    ATTR_MAP = {
        1: {
            "hp": 75,
            "dps": 50,
        },
        2: {
            "hp": 90,
            "dps": 70,
        },
        3: {
            "hp": 108,
            "dps": 90,
        },
        4: {
            "hp": 135,
            "dps": 125,
        },
        5: {
            "hp": 165,
            "dps": 170,
        },
    }

    def __init__(self, level):

        assert(1 <= level <= 5)
        
        super().__init__("Wizard", level)
        self.hp = self.ATTR_MAP[level]["hp"]
        self.preference = self.PREFER_GENERAL
        self.remHp = self.hp
        self.atkSpeed = 1500/MILISECONDS_PER_FRAME
        self.dph = self.ATTR_MAP[level]["dps"] * self.atkSpeed * MILISECONDS_PER_FRAME / 10e+3
        self.atkRange = 3
        self.movSpeed = 2 * MILISECONDS_PER_FRAME / 1000
        self.airTarget = True
        self.grndTarget = True
        self.isFlying = False

class TroopDirectory:

    TROOP_MAP = {
        "Barbarian": Barbarian,
        "Archer": Archer,
        "Giant": Giant,
        "Goblin": Goblin,
        "Wall Breaker": WallBreaker,
        "Balloon": Balloon,
        "Wizard": Wizard,
    }

    ALLOWED_TROOPS_MAP = {
        # Town Hall Level 1
        1: {
            "Barbarian": 1,
            "Archer": 0,
            "Giant": 0,
            "Goblin": 0,
            "Wall Breaker": 0,
            "Balloon": 0,
            "Wizard": 0,
        },
        # Town Hall Level 2
        2: {
            "Barbarian": 1,
            "Archer": 1,
            "Giant": 1,
            "Goblin": 1,
            "Wall Breaker": 0,
            "Balloon": 0,
            "Wizard": 0,
        },
        # Town Hall Level 3
        3: {
            "Barbarian": 2,
            "Archer": 2,
            "Giant": 1,
            "Goblin": 2,
            "Wall Breaker": 1,
            "Balloon": 0,
            "Wizard": 0,
        },
        # Town Hall Level 4
        4: {
            "Barbarian": 2,
            "Archer": 2,
            "Giant": 2,
            "Goblin": 2,
            "Wall Breaker": 2,
            "Balloon": 2,
            "Wizard": 0,
        },
        # Town Hall Level 5
        5: {
            "Barbarian": 3,
            "Archer": 3,
            "Giant": 2,
            "Goblin": 3,
            "Wall Breaker": 2,
            "Balloon": 2,
            "Wizard": 2,
        },
    }
  
    def __init__(self, townHallLevel: int):
        self.troopMap = {}
        self.townHallLevel = townHallLevel
        self.populateTroops()

    def getTroopCategoryIndex(self, troopName: str) -> int:
        """Returns the index of the troop in the list of allowed troops"""
        if troopName not in self.troopMap:
            return -1
        return list(TroopDirectory.ALLOWED_TROOPS_MAP[self.townHallLevel].keys()).index(troopName)

    def populateTroops(self):
        for troopName, level in TroopDirectory.ALLOWED_TROOPS_MAP[self.townHallLevel].items():
            if level > 0:
                self.troopMap[troopName] = level

    def getTroopObject(self, troopName: str) -> TroopBase:
        if troopName not in self.troopMap:
            return None
        return TroopDirectory.TROOP_MAP[troopName](self.getTroopLevel(troopName))
    
    @staticmethod
    def getTroopObjectStatic(troopName: str, townhall_level: int) -> TroopBase:
        if troopName not in TroopDirectory.TROOP_MAP:
            return None
        return TroopDirectory.TROOP_MAP[troopName](TroopDirectory.ALLOWED_TROOPS_MAP[townhall_level][troopName])

    def getAllTroopNames(self) -> List[str]:
        return list(self.troopMap.keys())
    
    def getTroopLevel(self, troopName: str) -> int:
        if troopName not in self.troopMap:
            return -1
        return self.troopMap[troopName]
    
    def getAll(self) -> List[TroopBase]:
        troops = []
        for troopName, level in self.troopMap.items():
            troops.append(TroopDirectory.TROOP_MAP[troopName](level))
        return troops
    
    @staticmethod
    def mapPreferenceToBuildingType(preference: int):
        if preference == TroopBase.PREFER_DEFENSE:
            return [BaseBuilding.TYPE_DEFENSE]
        
        elif preference == TroopBase.PREFER_RESOURCE:
            return [BaseBuilding.TYPE_RESOURCE, BaseBuilding.TYPE_TOWNHALL]
        
        elif preference == TroopBase.PREFER_GENERAL:
            return [
                    BaseBuilding.TYPE_DEFENSE,
                    BaseBuilding.TYPE_OTHERS,
                    BaseBuilding.TYPE_TOWNHALL,
                    BaseBuilding.TYPE_RESOURCE
                ]
        elif preference == TroopBase.PREFER_WALL:
            return [BaseBuilding.TYPE_WALL]
        
        else: return []

    
    def __str__(self):
        return ''.join([str(TroopDirectory.TROOP_MAP[troopName](level)) + '\n' for troopName, level in self.troopMap.items()])
