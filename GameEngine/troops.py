from .constants import *
import json
from typing import Dict, List

class TroopBase:

    LEVEL1 = 0x01
    LEVEL2 = 0x02
    LEVEL3 = 0x03
    LEVEL4 = 0x04
    LEVEL5 = 0x05
    LEVEL6 = 0x06
    LEVEL7 = 0x07
    LEVEL8 = 0x08
    LEVEL9 = 0x09

    BUILDING_PREFERENCE_GENERAL  = 0x01
    BUILDING_PREFERENCE_DEFENCE  = 0x02
    BUILDING_PREFERENCE_RESOURCE = 0x03
    BUILDING_PREFERENCE_WALL     = 0x04

    def __init__(self, name: str):

        self.name = name.title()
        self.id = None
        self.level = self.LEVEL1
        self.building_preference: int = TroopBase.BUILDING_PREFERENCE_GENERAL
        self.air_target: bool = None
        self.attack_range: int = None
        self.barrack_level: int = None
        self.attack_speed: int = None
        self.dps: List[int] = None
        self.housing_space: int = None
        self.hitpoints: List[int] = None
        self.laboratory_level: List[int] = None
        self.speed: int = None
        self.visual_level: List[int] = None
        self.ground_targets: bool = None
        self.air_target: bool = None
        self.is_flying: bool = None

        if self._load_obj() == -1:
            print(f"ERROR: Object `{self.name}` couldn't be created.")


    def _load_obj(self) -> int:
        
        with open(JSON_OBJECT_IDS_FILE, 'r') as f:
            id_data = dict(json.load(f))
            assert(self.name in id_data.keys())
            self.id = id_data[self.name]

        with open(JSON_CHARACTERS_FILE, 'r') as f:
            data = dict(json.load(f))
            
        if (self.name in data.keys()):
            if (self._contains_required_keys(data) is False): return -1
            data = dict(data[self.name])

            self.barrack_level = data['BarrackLevel'][0]
            self.attack_speed = data['AttackSpeed'][0]
            self.dps = data['DPS']
            self.housing_space = data['HousingSpace'][0]
            self.hitpoints = data['Hitpoints']
            self.laboratory_level = data['LaboratoryLevel']
            self.speed = data['Speed'][0]
            self.visual_level = data['VisualLevel']
            self.ground_targets = data['GroundTargets'][0]

            if 'AirTargets' in data.keys():
                self.air_target = data['AirTargets'][0]
            else:
                self.air_target = False
            if 'isFlying' in data.keys():
                self.is_flying = data['IsFlying'][0]
            else:
                self.is_flying = False
            if 'AttackRange' in data.keys():
                self.attack_range = data['AttackRange'][0]
            else:
                self.attack_range = 0


    def _contains_required_keys(self, data: Dict) -> bool:
        if (self.name not in data.keys()): return False

        troop_data = dict(data[self.name])

        required_keys = [
            'BarrackLevel',
            'AttackSpeed',
            'DPS',
            'HousingSpace',
            'Hitpoints',
            'LaboratoryLevel',
            'Speed',
            'VisualLevel',
            'GroundTargets',
            # 'AirTargets', # Not present in all the objects
            # 'IsFlying',   # Not present in all the objects
            # 'AttackRange' # Not present in all the objects
        ]

        for key in required_keys:
            if (key not in troop_data.keys()):
                print(f"ERROR: key `{key}` not found.")
                return False
        return True
    
    def max_level(self) -> int:
        if (self.visual_level and len(self.visual_level)):
            return self.visual_level[-1]
        
        return -1
    
    def set_level(self, level: int):
        assert TroopBase.LEVEL1 <= level <= self.max_level()
        self.level = level

    def __str__(self):
        return f"""Troop: {self.name}
    id: {self.id}
    level: {self.level}
    building_preference: {self.building_preference}
    air_target: {self.air_target}
    attack_range: {self.attack_range}
    barrack_level: {self.barrack_level}
    attack_speed: {self.attack_speed}
    dps: {self.dps}
    housing_space: {self.housing_space}
    hitpoints: {self.hitpoints}
    laboratory_level: {self.laboratory_level}
    speed: {self.speed}
    visual_level: {self.visual_level}
    ground_targets: {self.ground_targets}
    air_target: {self.air_target}
    is_flying: {self.is_flying}
"""
    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "level": self.level,
            "barrack_level": self.barrack_level,
            "attack_speed": self.attack_speed,
            "dps": self.dps[self.level - 1],
            "hitpoints": self.hitpoints[self.level - 1],
            "speed": self.speed,
            "housing_space": self.housing_space,
            "building_preference": self.building_preference,
            "air_target": self.air_target,
            "ground_targets": self.ground_targets,
            "is_flying": self.is_flying,
            "attack_range": self.attack_range
        } 



class Barbarian(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Barbarian")
        self.set_level(level)


class Archer(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Archer")
        self.set_level(level)


class Giant(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Giant")
        self.set_level(level)
        self.building_preference = self.BUILDING_PREFERENCE_DEFENCE


class Goblin(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Goblin")
        self.set_level(level)
        self.building_preference = self.BUILDING_PREFERENCE_RESOURCE


class WallBreaker(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Wall Breaker")
        self.set_level(level)
        self.building_preference = self.BUILDING_PREFERENCE_WALL


class Balloon(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Balloon")
        self.set_level(level)
        self.building_preference = self.BUILDING_PREFERENCE_DEFENCE


class Wizard(TroopBase):
    def __init__(self, level: int=TroopBase.LEVEL1):
        super().__init__("Wizard")
        self.set_level(level)

if __name__ == "__main__":
    barbarian = Barbarian(Barbarian.LEVEL3)
    archer = Archer(Archer.LEVEL1)
    giant = Giant(Giant.LEVEL6)
    wall_breaker = WallBreaker(WallBreaker.LEVEL1)
    balloon = Balloon(Balloon.LEVEL5)

    print(
        barbarian,
        archer,
        giant,
        wall_breaker,
        balloon,
        sep='\n')

