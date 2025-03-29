from .structures import *
from .troops import *
import numpy as np
import time

class SceneBase:

    BASE_HEIGHT     = 45
    BASE_WIDTH      = 45
    BASE_PADDING    = 2

    BASE_ORIGIN     = (0, 0)
    BASE_CENTER     = (22, 22)
    BASE_CORNER     = (44, 44)


    def __init__(self, town_hall_level: int=TownHall.LEVEL1):
        self.map = np.empty((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=object)

        self.placed_buildings = dict() # {ID[int]: (object)}
        self.placed_troops = dict() # {ID[int]: (object)}

        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                self.map[y, x] = {"building": -1, "troops": set()}
        
        self.town_hall_level = town_hall_level

        self.building_positions = {}  # Maps buildingID -> [(x, y)])

        self.buildings = AllStructures()
        self.placed_buildings_count = dict()
        self.buildings_max_count = dict()
        self.buildings_max_level = dict()

        self.troops = AllTroops()
        self.troops_max_level = dict()

        self.max_housing_space: int = 0
        self.current_housed_space: int = 0

        self.housed_troops = dict() # {ID[int]: (object)}

        self.total_building_hitpoints: int = 0
        self.current_building_hitpoints: int = 0

        self.start_time = -1
        self.current_time = -1
        self.total_time = 90   # in seconds

        self.stars = 0

        self.troopID_counter = 0

        self.load_scene_entity()

    def get_elasped_time(self):
        if self.current_time > self.start_time:
            return self.current_time - self.start_time
        return 0

    def get_rem_time(self) -> int:
        return self.total_time - int(self.get_elasped_time())

    def clear(self):
        self.placed_buildings.clear()
        self.placed_troops.clear()
        self.building_positions.clear()
        self.placed_buildings_count.clear()
        self.total_building_hitpoints = 0
        self.current_building_hitpoints = 0
        self.stars = 0

        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                self.map[y, x] = {"building": -1, "troops": set()}
        
        self.load_scene_entity()


    def load_scene_entity(self):
        with open(JSON_TOWNHALL_LEVELS_FILE, 'r') as f:
            data = list(json.load(f))
            assert(self.town_hall_level <= len(data))
            data = dict(data[self.town_hall_level - 1])
            for structure_name in self.buildings.structure_names:
                if structure_name in data.keys():
                    self.buildings_max_count[structure_name] = data[structure_name]
                    # Get the building max level for current TownHall level
                    _building = self.buildings.get(structure_name)
                    _levels = _building.get_allowed_levels(self.town_hall_level)
                    assert(len(_levels) > 0)
                    self.buildings_max_level[structure_name] = _levels[-1]
                else:
                    self.buildings_max_count[structure_name] = -1
                    self.buildings_max_level[structure_name] = -1
            
            self.buildings_max_count["Town Hall"] = 1
            self.buildings_max_level["Town Hall"] = TownHall.LEVEL5

            
            # Get the Laboratory level for TownHall level 5
            _laboratory = self.buildings.get("Laboratory")
            self.laboratory_level = _laboratory.get_allowed_levels(TownHall.LEVEL5)[-1]

            # Get the count of Camp Level for TownHall level 5
            _camp_count = self.buildings_max_count.get("Troop Housing")
            _max_camp_level = self.buildings_max_level.get("Troop Housing")
            _camp_space = self.buildings.get("Troop Housing").housing_space[_max_camp_level - 1]

            assert(_camp_count is not None)
            assert(_camp_space is not None)
            assert(_camp_count > 0)
            assert(_camp_space > 0)

            # Calculate the max housing space for troops
            self.max_housing_space = _camp_count * _camp_space

            for troop_name in self.troops.troop_names:
                troop = self.troops.get(troop_name)
                max_level = troop.get_max_allowed_level(self.laboratory_level)
                self.troops_max_level[troop_name] = max_level
                

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= x < self.BASE_WIDTH and 0 <= y < self.BASE_HEIGHT


    def is_tile_empty(self, y: int, x: int) -> bool:
        return self.in_bounds(y, x) and self.map[y, x] is None


    def place_building(self, building: BaseStructure, y, x):

        width = building.width
        height = building.height

        _buildingID = len(self.placed_buildings.keys())

        if not self.can_place_building(y, x, width, height):
            return False
        
        if (building.name not in self.placed_buildings_count.keys()):
            self.placed_buildings_count[building.name] = 0
        
        if (self.placed_buildings_count[building.name] + 1) > self.buildings_max_count[building.name]:
            print(f"WARNING: Building count exceeded for {building.name}")
            return False

        for dy in range(height):
            for dx in range(width):
                self.map[y + dy, x + dx]["building"] = _buildingID

        self.building_positions[_buildingID] = [(y + dy, x + dx) for dy in range(height) for dx in range(width)]
        building.position = (y, x)
        self.placed_buildings[_buildingID] = building
        self.placed_buildings_count[building.name] += 1
        if building.type != BaseStructure.CLASS_WALL:
            self.total_building_hitpoints += building.current_hitpoint
            self.current_building_hitpoints += building.current_hitpoint
        return True
    
    def get_damage_percentage(self):
        if self.total_building_hitpoints > 0:
            return 100.0 - round(self.current_building_hitpoints * 100 / self.total_building_hitpoints, 2)
        else:
            return 0.0
        
    def should_sim_stop(self):
        flag1 = self.stars == 3
        flag2 = (len(self.housed_troops.keys()) + len(self.placed_troops.keys())) == 0
        flag3 = self.get_rem_time() == 0

        return flag1 or flag2 or flag3
    

    def can_place_building(self, y, x, width, height):
        for dy in range(height):
            for dx in range(width):
                if not self.in_bounds(y + dy, x + dx):
                    print(f"WARNING: Building out of bounds at {y + dy}, {x + dx}")
                    return False
                if self.map[y + dy, x + dx]["building"] != -1:
                    print(f"WARNING: Building already exists at {y + dy}, {x + dx}")
                    return False
        return True
    
    def get_stars(self):
        return self.stars
    

    def recruit_troop(self, troop: TroopBase):
        if (self.current_housed_space + troop.housing_space) > self.max_housing_space:
            print("WARNING: Housing space exceeded")
            return
        
        self.housed_troops[self.troopID_counter] = troop
        self.current_housed_space += troop.housing_space
        self.troopID_counter += 1

    def disband_troop(self, troopID: int):
        if troopID not in self.housed_troops:
            return
        troop = self.housed_troops[troopID]
        self.current_housed_space -= troop.housing_space
        del self.housed_troops[troopID]
        

    def place_troop(self, _troopID: int, y: int, x: int):
        if not self.in_bounds(y, x):
            return False
        
        if _troopID not in self.housed_troops:
            return False
        
        if _troopID in self.placed_troops:
            return False
        
        troop = self.housed_troops[_troopID]
        self.map[y, x]["troops"].add(_troopID)
        troop.current_position = (y, x)

        self.placed_troops[_troopID] = troop
        self.disband_troop(_troopID)

        return True
    
    def destroy_building(self, buildingID: int):
        if buildingID not in self.placed_buildings:
            return
        for y, x in self.building_positions[buildingID]:
            self.map[y, x]["building"] = -1

        building = self.placed_buildings[buildingID]

        if building.name == "Town Hall":
            self.stars += 1

        prev_damage_percentage = self.get_damage_percentage()

        self.placed_buildings_count[building.name] -= 1
        if building.type != BaseStructure.CLASS_WALL:
            self.current_building_hitpoints -= building.max_hitpoints()

        if self.get_damage_percentage() >= 50.0 and prev_damage_percentage < 50.0:
            self.stars += 1

        if self.get_damage_percentage() == 100.0:
            self.stars = 3
            
        del building
        del self.building_positions[buildingID]
        del self.placed_buildings[buildingID]
    
    def remove_building(self, buildingID: int):
        if buildingID not in self.placed_buildings:
            return
        for y, x in self.building_positions[buildingID]:
            self.map[y, x]["building"] = -1

        building = self.placed_buildings[buildingID]
        self.placed_buildings_count[building.name] -= 1
        if building.type != BaseStructure.CLASS_WALL:
            self.current_building_hitpoints -= building.max_hitpoints()
            self.total_building_hitpoints -= building.max_hitpoints()
        
        del building
        del self.building_positions[buildingID]
        del self.placed_buildings[buildingID]

    
    def update_level(self, buildingID: int, level: int):
        if buildingID not in self.placed_buildings:
            return
        building = self.placed_buildings[buildingID]
        prev_hitpoint  = building.max_hitpoints()
        building.set_level(level)

        if building.type != BaseStructure.CLASS_WALL:
            self.current_building_hitpoints -= prev_hitpoint
            self.total_building_hitpoints -= prev_hitpoint

            self.current_building_hitpoints += building.max_hitpoints()
            self.total_building_hitpoints += building.max_hitpoints()


    def generate_troop_mask(self, flying:bool = False) -> np.ndarray:
        troop_mask = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=bool)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                troopID_set = self.map[y, x]["troops"]
                if len(troopID_set) == 0:
                    troop_mask[y, x] = 0
                else:
                    for troopID in troopID_set:
                        troop = self.placed_troops[troopID]
                        if flying:
                            if troop.is_flying:
                                troop_mask[y, x] = 1
                                break
                        else:
                            if not troop.is_flying:
                                troop_mask[y, x] = 1
                                break 
        return troop_mask
    

    def generate_troop_label(self, flying=False) -> np.ndarray:
        troop_label = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=int)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                troop_label[y, x] = -1
                troopID_set = self.map[y, x]["troops"]
                if len(troopID_set) == 0:
                    continue
                for troopID in troopID_set:
                    troop = self.placed_troops[troopID]
                    if flying:
                        if troop.is_flying:
                            troop_label[y, x] = troopID
                            break
                    else:
                        if not troop.is_flying:
                            troop_label[y, x] = troopID
                            break
        return troop_label


    def generate_wall_mask(self) -> np.ndarray:
        wall_mask = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=bool)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                buildingID = self.map[y, x]["building"]
                if buildingID != -1:
                    building = self.placed_buildings[buildingID]
                    if building.name == "Wall":
                        wall_mask[y, x] = True
        return wall_mask
    

    def generate_resource_mask(self) -> np.ndarray:
        resource_mask = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=bool)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                buildingID = self.map[y, x]["building"]
                if buildingID != -1:
                    building = self.placed_buildings[buildingID]
                    if building.type == BaseStructure.CLASS_RESOURCE or building.name == "Town Hall":
                        resource_mask[y, x] = True
        return resource_mask
    

    def generate_defense_mask(self) -> np.ndarray:
        defense_mask = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=bool)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                buildingID = self.map[y, x]["building"]
                if buildingID != -1:
                    building = self.placed_buildings[buildingID]
                    if building.type == BaseStructure.CLASS_DEFENSE:
                        defense_mask[y, x] = True
        return defense_mask
    

    def generate_general_mask(self) -> np.ndarray:
        general_mask = np.zeros((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=bool)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                buildingID = self.map[y, x]["building"]
                if buildingID != -1:
                    building = self.placed_buildings[buildingID]
                    if building.type == BaseStructure.CLASS_OTHERS:
                        general_mask[y, x] = True
        return general_mask
    

    def generate_all_mask(self) -> np.ndarray:
        _wall_mask = self.generate_wall_mask()
        _resource_mask = self.generate_resource_mask()
        _defense_mask = self.generate_defense_mask()
        _general_mask = self.generate_general_mask()
        all_mask = (_wall_mask << 3) | (_general_mask << 2) | (_resource_mask << 1) | _defense_mask
        return all_mask


    def kill_troop(self, troopID: int):
        if troopID not in self.placed_troops:
            return
        troop = self.placed_troops[troopID]
        assert(isinstance(troop, TroopBase))
        y, x = troop.current_position
        self.map[y, x]["troops"].remove(troopID)
        del self.placed_troops[troopID]


    def transition(self):

        self.current_time = time.time()

        # Check if Townhall is placed
        if "Town Hall" not in self.placed_buildings_count:
            print("WARNING: Town Hall not placed")
            return

        destroyed_buildings = set()
        targeted_buildings = dict()

        # Transition all the troops 
        for troopID, troop in self.placed_troops.items():
            y, x = troop.current_position
            self.map[y, x]["troops"].remove(troopID)

            attack = troop.transition(self.generate_all_mask())

            current_target = troop.current_target
            target_wall = troop.target_wall
            
            if current_target is None:
                print(f"WARNING: Troop {troop.name} has no target")
            else:

                _buildingID = self.map[current_target]["building"]
                _wallID = self.map[target_wall]["building"] if target_wall else -1

                if _buildingID in targeted_buildings:
                    targeted_buildings[_buildingID].append(troop)
                else:
                    targeted_buildings[_buildingID] = [troop]

                if _wallID in targeted_buildings:
                    targeted_buildings[_wallID].append(troop)
                else:
                    targeted_buildings[_wallID] = [troop]

                if attack:
                    # If the troop attack the 
                    if _wallID != -1:
                        building = self.placed_buildings[_wallID]
                        building.current_hitpoint -=  attack * troop.attack_damage() * troop.max_attack_timer/3000
                        if building.current_hitpoint <= 0:
                            destroyed_buildings.add(_wallID)
                        
                    elif _buildingID != -1:
                        building = self.placed_buildings[_buildingID]
                        building.current_hitpoint -=  attack * troop.attack_damage() * troop.max_attack_timer/3000
                        if building.current_hitpoint <= 0:
                            destroyed_buildings.add(_buildingID)

            y, x = troop.current_position
            self.map[y, x]["troops"].add(troopID)

        # Handle All the destroyed buildings
        for buildingID in destroyed_buildings:
            for troop in targeted_buildings[buildingID]:
                troop.revoke()
            self.destroy_building(buildingID)

        troop_mask_flying = self.generate_troop_mask(flying=True)
        troop_mask_ground = self.generate_troop_mask(flying=False)
        troop_mask = troop_mask_flying | troop_mask_ground

        troop_label_flying = self.generate_troop_label(flying=True)
        troop_label_ground = self.generate_troop_label(flying=False)
        troop_label = np.maximum(troop_label_flying, troop_label_ground)

        # Transition all the left buildings
        dead_troops = dict()
        for buildingID, building in self.placed_buildings.items():
            assert(isinstance(building, BaseStructure))
            if (building.type == BaseStructure.CLASS_DEFENSE):
                assert(isinstance(building, DefenseStructure))
                hit = None
                if building.air_targets and not building.ground_targets:
                    hit = building.transition(troop_mask_flying, troop_label_flying)
                elif not building.air_targets and building.ground_targets:
                    hit = building.transition(troop_mask_ground, troop_label_ground)
                else:           
                    hit = building.transition(troop_mask, troop_label)
                    
                assert(hit is not None)

                if hit:
                    targeted_troop = building.current_target_troop_id
                    if targeted_troop in self.placed_troops:
                        troop = self.placed_troops[targeted_troop]
                        assert(isinstance(troop, TroopBase))
                        troop.current_hitpoint = troop.current_hitpoint - building.damage() * building.max_attack_timer / 3000
                        if (troop.current_hitpoint <= 0):
                            if targeted_troop in dead_troops:
                                dead_troops[targeted_troop].append(buildingID)
                            else:
                                dead_troops[targeted_troop] = [buildingID]
    
        for troopID, buildingIDs in dead_troops.items():
            troop = self.placed_troops[troopID]
            self.kill_troop(troopID)
            for buildingID in buildingIDs:
                building = self.placed_buildings[buildingID]
                building.revoke()


    def __str__(self):
        return f"""
SceneBase:
    TownHall Level: {self.town_hall_level}
    Buildings:
        {self.placed_buildings}
    Troops:
        {self.placed_troops}
"""