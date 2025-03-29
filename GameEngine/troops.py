import random
import math
from .constants import *
import json
import numpy as np
from typing import Dict, List
import heapq

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

    IMAGE_MAP = {
        "Barbarian": PATH_IMAGE_BARBARIAN,
        "Archer": PATH_IMAGE_ARCHER,
        "Giant": PATH_IMAGE_GIANT,
        "Goblin": PATH_IMAGE_GOBLIN,
        "Wall Breaker": PATH_IMAGE_WALL_BREAKER,
        "Balloon": PATH_IMAGE_BALLOON,
        "Wizard": PATH_IMAGE_WIZARD
    }

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
        self.image_path: str = None

        self.current_target: int = None
        self.target_wall: int = None    # Seperate Logic for Breaking Walls

        self.current_hitpoint = -1

        self.path: List[tuple] = []
        self.current_position: tuple = (-1, -1)

        self.move_timer = 0
        self.max_move_timer = -1
        self.attack_timer = 0
        self.max_attack_timer = -1

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

            self.image_path = TroopBase.IMAGE_MAP[self.name] if self.name in TroopBase.IMAGE_MAP.keys() else ''
            self.max_attack_timer = self.attack_speed
            self.max_move_timer = math.ceil(3000.0 / self.speed)

            if 'AirTargets' in data.keys():
                self.air_target = data['AirTargets'][0]
            else:
                self.air_target = False
            if 'IsFlying' in data.keys():
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
        max_lvl = self.max_level()
        if level > max_lvl:
            print(f"WARNING: Level {level} exceeds max {max_lvl}, setting to max.")
            level = max_lvl
        self.level = level
        self.current_hitpoint = self.hitpoints[self.level - 1]

    def get_max_allowed_level(self, laboratory_level: int) -> int:
        if (laboratory_level < 0 or laboratory_level >= len(self.laboratory_level)):
            return -1
        max_level = 0
        for level in zip(self.laboratory_level, self.visual_level):
            if level[0] == laboratory_level:
                return level[1]
            elif level[0] < laboratory_level:
                max_level = level[1]
            else:
                break
        return max_level
    
    def get_next_tile(self) -> tuple:
        if not len(self.path):
            return self.current_position
        return self.path[-1]


    def can_attack_air(self) -> bool:
        return self.air_target

    def can_attack_ground(self) -> bool:
        return self.ground_targets
    
    def attack_damage(self) -> int:
        return self.dps[self.level - 1]
    
    def get_attack_speed(self) -> int:
        return self.attack_speed
    
    def get_max_hit_point(self) -> int:
        return self.hitpoints[self.level -1]
    
    def revoke(self):
        self.current_target = None
        self.path = []
        self.target_wall = None
    
    def find_closest_target(self, scene_mask, start_y, start_x):
        """
        Finds the closest target based on troop preference (resource, defense, general).
        Returns the (x, y) coordinates of the closest target or None if none are found.
        """
        target_mask = None

        if self.building_preference == self.BUILDING_PREFERENCE_RESOURCE:
            target_mask = scene_mask == 2
        elif self.building_preference == self.BUILDING_PREFERENCE_DEFENCE:
            target_mask = scene_mask == 1
        elif self.building_preference == self.BUILDING_PREFERENCE_WALL:
            target_mask = scene_mask == 8
        else:
            target_mask = (scene_mask == 1) | (scene_mask == 2) | (scene_mask == 4)

        target_positions = np.argwhere(target_mask)

        # If target positions is all zero
        if not len(target_positions):
            target_mask = (scene_mask == 1) | (scene_mask == 2) | (scene_mask == 4)
            target_positions = np.argwhere(target_mask)
            if not len(target_positions):
                self.current_target = None
                return
    
        closest_target = min(target_positions, key=lambda pos: (pos[0] - start_y)**2 + (pos[1] - start_x)**2)
        self.current_target = tuple(closest_target)
    
    def transition(self, scene_mask: np.ndarray) -> bool:
        """
        Moves the troop towards its target or attacks a wall if blocked.
        Returns if Damage is dealt to the target.
        """

        if self.current_target is None:
            self.find_closest_target(scene_mask, self.current_position[0], self.current_position[1])
            if self.current_target is None:
                return False

        if self.inRange(self.current_target[0], self.current_target[1], self.attack_range/100):
            if (self.attack_timer == 0):
                self.attack_timer = (self.attack_timer + 100) % self.max_attack_timer
                return True
            else:
                self.attack_timer = (self.attack_timer + 100) % self.max_attack_timer
                return False

        elif self.target_wall is not None:
            if self.inRange(self.target_wall[0], self.target_wall[1], self.attack_range/100):
                if (self.attack_timer == 0):
                    self.attack_timer = (self.attack_timer + 100) % self.max_attack_timer
                    return True
                else:
                    self.attack_timer = (self.attack_timer + 100) % self.max_attack_timer
                    return False
            else:
                self.move_toward_target()
                return False

        if not len(self.path):
            self.find_path(scene_mask)
            if not len(self.path):
                self.find_path_with_wall(scene_mask)


        self.move_toward_target()
        return False
    

    def find_path_with_wall(self, scene_mask: np.ndarray):
        start_y, start_x = self.current_position
        open_set = [(0, start_y, start_x)]
        came_from = {}
        g_score = { (start_y, start_x): 0 }
        f_score = { (start_y, start_x): self.octile_distance(start=(start_y, start_x), goal=self.current_target) }

        self.path.clear()
        while open_set:
            _, y, x = heapq.heappop(open_set)
            if self.current_target == (y, x):
                break

            if scene_mask[y, x] == 8:
                self.target_wall = (y, x)
                break
            
            neibs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            random.shuffle(neibs)
            for dx, dy in neibs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < scene_mask.shape[1] and 0 <= ny < scene_mask.shape[0]:
                    cost = g_score[(y, x)] + 1

                    if (ny, nx) not in g_score or cost < g_score[(ny, nx)]:
                        g_score[(ny, nx)] = cost
                        f_score[(ny, nx)] = cost + self.octile_distance(start=(ny, nx), goal=self.current_target)
                        heapq.heappush(open_set, (f_score[(ny, nx)], ny, nx))
                        came_from[(ny, nx)] = (y, x)

        if (self.target_wall not in came_from):
            # Path not found [Try Wall Breaking Mode]
            return
        
        current = self.target_wall
        while current != (start_y, start_x):
            current = came_from[current]
            self.path.append(current)

    @staticmethod   
    def octile_distance(start, goal, D=1, D2=math.sqrt(1)):
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * max(dx, dy) + (D2 - D) * min(dx, dy)
        
    
    def find_path(self, scene_mask: np.ndarray):
        start_y, start_x = self.current_position
        open_set = [(0, start_y, start_x)]
        came_from = {}
        g_score = { (start_y, start_x): 0 }
        f_score = { (start_y, start_x): abs(self.current_target[0] - start_x) + abs(self.current_target[1] - start_y) }

        self.path.clear()
        while open_set:
            _, y, x = heapq.heappop(open_set)
            if self.current_target == (y, x):
                break
            
            neibs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            random.shuffle(neibs)
            for dx, dy in neibs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < scene_mask.shape[1] and 0 <= ny < scene_mask.shape[0]:
                    cost = g_score[(y, x)] + 1

                    if scene_mask[ny, nx] == 8 and not self.is_flying:
                        # Case of wall; Flying troops will ignore it
                        continue

                    if (ny, nx) not in g_score or cost < g_score[(ny, nx)]:
                        g_score[(ny, nx)] = cost
                        f_score[(ny, nx)] = cost + abs(self.current_target[0] - nx) + abs(self.current_target[1] - ny)
                        heapq.heappush(open_set, (f_score[(ny, nx)], ny, nx))
                        came_from[(ny, nx)] = (y, x)

        if (self.current_target not in came_from):
            # Path not found [Try Wall Breaking Mode]
            return
        
        current = self.current_target
        while current != (start_y, start_x):
            self.path.append(current)
            current = came_from[current]
    
    def move_toward_target(self):
        if len(self.path):
            # Move towards the target
            if (self.move_timer == self.max_move_timer - 1):
                next_tile = self.path.pop()
                self.current_position = next_tile
            self.move_timer = (self.move_timer + 1) % self.max_move_timer


    def inRange(self, target_y: int, target_x: int, _range: int = 1) -> bool:
        return np.linalg.norm([target_y - self.current_position[0], target_x - self.current_position[1]]) <= _range

    def __str__(self):
        return f"""Troop: {self.name}
    id: {self.id}
    level: {self.level}
    building_preference: {self.building_preference}
    image_path: {self.image_path}
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


class AllTroops:
    def __init__(self):
        self.barbarian = Barbarian()
        self.archer = Archer()
        self.giant = Giant()
        self.goblin = Goblin()
        self.wall_breaker = WallBreaker()
        self.balloon = Balloon()
        self.wizard = Wizard()

        self.troop_names = [
            self.barbarian.name,
            self.archer.name,
            self.giant.name,
            self.goblin.name,
            self.wall_breaker.name,
            self.balloon.name,
            self.wizard.name
        ]

    def get(self, name: str) -> TroopBase:
        if name == "Barbarian":
            return self.barbarian
        elif name == "Archer":
            return self.archer
        elif name == "Giant":
            return self.giant
        elif name == "Goblin":
            return self.goblin
        elif name == "Wall Breaker":
            return self.wall_breaker
        elif name == "Balloon":
            return self.balloon
        elif name == "Wizard":
            return self.wizard
        else:
            return None
        
    def all_troops(self) -> List[TroopBase]:
        return [
            self.barbarian,
            self.archer,
            self.giant,
            self.goblin,
            self.wall_breaker,
            self.balloon,
            self.wizard
        ]

    def __str__(self):
        return f"""All Troops:
    Barbarian: {self.barbarian}
    Archer: {self.archer}
    Giant: {self.giant}
    Goblin: {self.goblin}
    Wall Breaker: {self.wall_breaker}
    Balloon: {self.balloon}
    Wizard: {self.wizard}
"""

    def from_dict(self, data: Dict):
        self.barbarian = Barbarian()
        self.archer = Archer()
        self.giant = Giant()
        self.goblin = Goblin()
        self.wall_breaker = WallBreaker()
        self.balloon = Balloon()
        self.wizard = Wizard()

        self.barbarian.level = data["Barbarian"]["level"]
        self.archer.level = data["Archer"]["level"]
        self.giant.level = data["Giant"]["level"]
        self.goblin.level = data["Goblin"]["level"]
        self.wall_breaker.level = data["Wall Breaker"]["level"]
        self.balloon.level = data["Balloon"]["level"]

