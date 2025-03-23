from .constants import *
from typing import List, Dict
import json

class BaseStructure:

    LEVEL1 = 0x01
    LEVEL2 = 0x02
    LEVEL3 = 0x03
    LEVEL4 = 0x04
    LEVEL5 = 0x05
    LEVEL6 = 0x06
    LEVEL7 = 0x07
    LEVEL8 = 0x08
    LEVEL9 = 0x09

    CLASS_DEFENSE   = 0x01
    CLASS_RESOURCE  = 0x02
    CLASS_WALL      = 0x05
    CLASS_OTHERS    = 0x06

    def __init__(self, name: str):
        self.name: str = name.title()
        self.id = ''
        self.level: int = BaseStructure.LEVEL1
        self.type: int = BaseStructure.CLASS_OTHERS
        self.width: int = None
        self.height: int = None
        self.building_levels: List[int] = None
        self.hitpoints: List[int] = None
        self.townhall: List[int] = None

    def contains_required_keys(self, obj: dict = None) -> bool:
        if (obj is None): return False
        required_keys = [
            'Height',
            'Width',
            'Hitpoints',
            'BuildingLevel',
            'TownHallLevel'
        ]
        for key in required_keys:
            if (key not in obj.keys()):
                print(f"ERROR: Object `{self.name}` does not contain property `{key}`.")
        return True
    
    def load_obj(self, obj: dict = None) -> int:
        if not isinstance(obj, dict): 
            with open(JSON_BUILDINGS_FILE, 'r') as f:
                obj = dict(json.load(f))[self.name]
            if not isinstance(obj, dict):
                print(f"ERROR: Failed to load json file for {self.name}")
                return -1
            
        if not self.contains_required_keys(obj):
            print(f"ERROR: Object `{self.name}` does not contains required keys.")
            return -1
        
        self.width = obj['Width'][0]
        self.height = obj['Height'][0]
        self.building_levels = obj['BuildingLevel']
        self.townhall = obj['TownHallLevel']
        self.hitpoints = obj['Hitpoints']
        return 0

    def get_max_level(self) -> int:
        if (self.building_levels and len(self.building_levels)):
            return self.building_levels[-1]
        return -1
    
    def set_level(self, level: int) -> bool:
        if (level in range(1, self.get_max_level())):
            self.level = level
            return True
        return False    

    def __str__(self):
        return f"""Building:
    name: {self.name}
    id: {self.id}
    level: {self.level}
    type: {self.type}
    width: {self.width}
    height: {self.height}
    building_levels: {self.building_levels}
    hitpoints: {self.hitpoints}
    townhall: {self.townhall}"""  


class DefenseStructure(BaseStructure):
    def __init__(self, name):
        super().__init__(name)
        self.type = BaseStructure.CLASS_DEFENSE
        self.dps: List[int] = None
        self.ground_targets: bool = None
        self.air_targets: bool = None
        self.attack_speed: int = None
        self.max_attack_range: int = None
        self.damage_radius: List[int] = None
        self.push_back: List[int] = None
        self.min_attack_range: int = None

    def contains_required_keys(self, obj: dict = None) -> bool:
        if obj is None: return False
        if not super().contains_required_keys(obj): return False
        required_keys = [
            'DPS',
            'AttackRange',
            'AttackSpeed',
            # 'GroundTargets',  # Not present in all children
            # 'AirTargets',     # Not present in all children
            # 'DamageRadius',   # Not present in all children
            # 'MinAttackRange', # Not present in all children
            # 'PushBack'        # Not present in all children
        ]
        for key in required_keys:
            if (key not in obj.keys()): return False
        return True

    def load_obj(self, obj = None) -> int:
        if not isinstance(obj, dict):
            with open(JSON_BUILDINGS_FILE, 'r') as f:
                obj = dict(json.load(f))[self.name]
            if not isinstance(obj, dict):
                print(f"ERROR: Failed to load json file for {self.name}")
                return -1
            
        if super().load_obj(obj) == -1: return -1
        if not self.contains_required_keys(obj): return -1

        self.dps = obj['DPS']
        self.attack_speed = obj['AttackSpeed'][0]
        self.max_attack_range = obj['AttackRange'][0]
        self.ground_targets = obj['GroundTargets'][0] if 'GroundTargets' in obj.keys() else False
        self.air_targets = obj['AirTargets'][0] if 'AirTargets' in obj.keys() else False
        self.damage_radius = obj['DamageRadius'] if 'DamageRadius' in obj.keys() else [0 for i in self.building_levels]
        self.min_attack_range = obj['MinAttackRange'][0] if 'MinAttackRange' in obj.keys() else 0
        self.push_back = obj['PushBack'] if 'PushBack' in obj.keys() else [0 for i in self.building_levels]
        return 0
    
    def __str__(self):
        return super().__str__() + f"""
    dps: {self.dps}
    ground_targets: {self.ground_targets}
    air_targets: {self.air_targets}
    attack_speed: {self.attack_speed}
    max_attack_range: {self.max_attack_range}
    damage_radius: {self.damage_radius}
    push_back: {self.push_back}
    min_attack_range: {self.min_attack_range}"""

class ResourceStructure(BaseStructure):

    CLASS_STORE_ELIXIR  = 0x01
    CLASS_STORE_GOLD    = 0x02
    CLASS_STORE_BOTH    = 0x03
    
    def __init__(self, name: str, resource_type: int):
        super().__init__(name)
        self.type = BaseStructure.CLASS_RESOURCE
        self.resource_type = resource_type
        self.max_stored_gold: List[int] = None
        self.max_stored_elixir: List[int] = None
        self.current_stored_gold: int = -1
        self.current_stored_elixir: int = -1

    def contains_required_keys(self, obj: dict = None) -> bool:
        if obj is None: return False
        if not super().contains_required_keys(obj): return False
        required_keys = [
            'ResourceMax',
            'MaxStoredGold',
            'MaxStoredElixir',
        ]
        if all([(key in obj.keys())==False for key in required_keys]): return False
        return True
    
    def load_obj(self, obj: dict = None):
        if not isinstance(obj, dict):
            with open(JSON_BUILDINGS_FILE, 'r') as f:
                obj = dict(json.load(f))[self.name]
            if not isinstance(obj, dict):
                print(f"ERROR: Failed to load json file for {self.name}")
                return -1

        if super().load_obj(obj) == -1: return -1
        if not self.contains_required_keys(obj): return -1

        if 'ResourceMax' in obj.keys():
            self.max_stored_elixir = self.max_stored_gold = obj['ResourceMax']
            if (self.resource_type == ResourceStructure.CLASS_STORE_GOLD):
                self.max_stored_elixir = [0 for i in self.building_levels]
            elif (self.resource_type == ResourceStructure.CLASS_STORE_ELIXIR):
                self.max_stored_gold = [0 for i in self.building_levels]

        elif 'MaxStoredGold' in obj.keys() and self.resource_type == ResourceStructure.CLASS_STORE_GOLD:
            self.max_stored_gold = obj['MaxStoredGold']
            self.max_stored_elixir = [0 for i in self.building_levels]

        elif 'MaxStoredElixir' in obj.keys() and self.resource_type == ResourceStructure.CLASS_STORE_ELIXIR:
            self.max_stored_elixir = obj['MaxStoredElixir']
            self.max_stored_gold = [0 for i in self.building_levels]

        elif 'MaxStoredGold' in obj.keys() and 'MaxStoredElixir' in obj.keys() and self.resource_type == ResourceStructure.CLASS_STORE_BOTH:
            self.max_stored_gold = obj['MaxStoredGold']
            self.max_stored_elixir = obj['MaxStoredElixir']
            
        else:
            print(f"ERROR: Resource constraint failed for `{self.name}`.")
            return -1
        
        self.current_stored_elixir = self.current_stored_gold =0

        return 0
    
    def __str__(self):
        return super().__str__() + f"""
    resource_type: {self.resource_type}
    max_stored_gold: {self.max_stored_gold}
    max_stored_elixir: {self.max_stored_elixir}
    current_stored_gold: {self.current_stored_gold}
    current_stored_elixir: {self.current_stored_elixir}"""
    

class TownHall(ResourceStructure):
    def __init__(self, level: int = ResourceStructure.LEVEL1, obj: dict = None):
        super().__init__("Town Hall", ResourceStructure.CLASS_STORE_BOTH)

        super().load_obj(obj)
        self.set_level(level)


class AllianceCastle(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Alliance Castle")
        self.housing_space: int = None
        self.type = AllianceCastle.CLASS_CASTLE

        self.load_obj(obj)
        self.set_level(level)



    def contains_required_keys(self, obj: dict = None) -> bool:
        if obj is None: return False
        if not super().contains_required_keys(obj): return False
        required_keys = [
            'HousingSpace',
        ]
        for key in required_keys:
            if key not in obj.keys():
                return False
        return True
    
    def load_obj(self, obj = None):
        if not isinstance(obj, dict):
            with open(JSON_BUILDINGS_FILE, 'r') as f:
                obj = dict(json.load(f))[self.name]
            if not isinstance(obj, dict):
                print(f"ERROR: Failed to load json file for {self.name}")
                return -1
        if not super().load_obj(obj): return -1
        self.housing_space = obj['HousingSpace']
        return 0


class Wall(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Wall")
        self.type = Wall.CLASS_WALL
        super().load_obj(obj)
        self.set_level(level)


class TroopHousing(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Troop Housing")

        super().load_obj(obj)
        self.set_level(level)


class Barrack(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Barrack")

        super().load_obj(obj)
        self.set_level(level)


class Laboratory(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Laboratory")

        super().load_obj(obj)
        self.set_level(level)


class SpellForge(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Spell Forge")

        super().load_obj(obj)
        self.set_level(level)


class BuilderHome(BaseStructure):
    def __init__(self, level: int = BaseStructure.LEVEL1, obj: dict = None):
        super().__init__("Builder6Home")

        super().load_obj(obj)
        self.set_level(level)


class ElixirPump(ResourceStructure):
    def __init__(self, level: int = ResourceStructure.LEVEL1, obj: dict = None):
        super().__init__('Elixir Pump')
        self.resource_type = ResourceStructure.CLASS_RESOURCE_ELIXIR

        super().load_obj(obj)
        self.set_level(level)
    

class GoldMine(ResourceStructure):
    def __init__(self, level: int = ResourceStructure.LEVEL1, obj: dict = None):
        super().__init__('Gold Mine')
        self.resource_type = ResourceStructure.CLASS_RESOURCE_GOLD

        super().load_obj(obj)
        self.set_level(level)


class ElixirStorage(ResourceStructure):
    def __init__(self, level: int = ResourceStructure.LEVEL1, obj: dict = None):
        super().__init__('Elixir Storage')
        self.resource_type = ResourceStructure.CLASS_RESOURCE_ELIXIR

        super().load_obj(obj)
        self.set_level(level)


class GoldStorage(ResourceStructure):
    def __init__(self, level: int = ResourceStructure.LEVEL1, obj: dict = None):
        super().__init__('Gold Storage')
        self.resource_type = ResourceStructure.CLASS_RESOURCE_GOLD

        super().load_obj(obj)
        self.set_level(level)


class Cannon(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Cannon")

        super().load_obj(obj)
        self.set_level(level)


class ArcherTower(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Archer Tower")

        super().load_obj(obj)
        self.set_level(level)


class Mortar(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Mortar")

        super().load_obj(obj)
        self.set_level(level)


class Cannon(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Cannon")

        super().load_obj(obj)
        self.set_level(level)


class AirDefense(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Air Defense")

        super().load_obj(obj)
        self.set_level(level)


class WizardTower(DefenseStructure):
    def __init__(self, level: int = DefenseStructure.LEVEL1, obj: dict = None):
        super().__init__("Wizard Tower")
        
        super().load_obj(obj)
        self.set_level(level)
