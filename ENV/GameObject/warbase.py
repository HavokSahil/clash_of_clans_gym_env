import random
import numpy as np
from .buildings import *
from typing import List, Tuple
import matplotlib.pyplot as plt
from .config import *

class Position:
    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    def __str__(self):
        return f"({self.y}, {self.x})"

    def __repr__(self):
        return f"({self.y}, {self.x})"

class Base:
    
    HEIGHT_WORLD = BASE_WIDTH
    WIDTH_WORLD = BASE_WIDTH
    PADDING_WORLD = BASE_PADDING

    GRID_MAPPING = {
        "buildingID": 0,
        "building_type": 1,
        "building_level": 2,
        "building_remaining_hp": 3,
        "gold": 4,
        "elixir": 5,
        "building_object_identifier": 6,
        "building_allowed_position": 7,
        "building_min_atk_range": 8,
        "building_max_atk_range": 9,
        "building_dph": 10,
        "building_atk_speed": 11,
        "building_target_domain": 12,
        "target_troop_id": 13,
        "steps_since_last_shoot": 14
    }

    def __init__(self, townHallLevel: int = 1):
        self.world = np.ones((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int) * -1
        self.townHallLevel      = townHallLevel
        self.buildingDirectory  = BuildingDirectory(self.townHallLevel)
        self.placedBuildings    = dict()   # ID: Tuple[Object[Building], Position]
        self.buildingCount      = dict()     # Type: Count

        self.id_gen_param = 1

    def clear(self):
        self.world = np.ones((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int) * -1
        self.buildingDirectory  = BuildingDirectory(self.townHallLevel)
        self.placedBuildings.clear()
        self.buildingCount.clear()

    def getBuildingCount(self, name):
        return self.buildingCount.get(name, 0)
    
    def getBuildingMaxCount(self, name):
        return self.buildingDirectory.getBuildingMaxCount(name)
    
    def getBuildingObject(self, name):
        return self.buildingDirectory.getBuildingObject(name)

    def getAvailableBuidlings(self):
        availableBuildings = []
        for name in self.buildingDirectory.getAllBuildingNames():
            if self.getBuildingCount(name) < self.getBuildingMaxCount(name):
                availableBuildings.append((name, self.buildingDirectory.getBuildingLevel(name)))
            
        return availableBuildings
    
    def getAllBuildings(self):
        allBuildings = []
        for name in self.buildingDirectory.getAllBuildingNames():
            allBuildings.append((name, self.buildingDirectory.getBuildingLevel(name)))
        return [(name, level) for name, level in allBuildings if level > 0]

    def isTileEmpty(self, y: int, x: int):
        return self.world[y, x] == -1
    
    def isTileValid(self, y: int, x: int):
        return self.PADDING_WORLD <= y < (self.HEIGHT_WORLD - self.PADDING_WORLD) and self.PADDING_WORLD <= x < (self.WIDTH_WORLD - self.PADDING_WORLD)

    def canPlaceBuilding(self, building: BaseBuilding, y: int, x: int, _debug=False):
        # Check if the building can be placed on the tile
        for i in range(building.height):
            for j in range(building.width):
                if not self.isTileValid(y + i, x + j):
                    if _debug:
                        print(f"Tile ({y + i}, {x + j}) is not valid")
                    return False
                if not self.isTileEmpty(y + i, x + j):
                    if _debug:
                        print(f"Tile ({y + i}, {x + j}) is not empty")
                    return False  

        return True        

    def genBuildingId(self):
        ret_id = self.id_gen_param
        self.id_gen_param += 1
        return ret_id

    def placeBuilding(self, building: BaseBuilding, y: int, x: int, _debug=False) -> bool:

        if not self.canPlaceBuilding(building, y, x, _debug):
            return False
        
        buildingId = self.genBuildingId()

        if self.getBuildingCount(building.name) >= self.getBuildingMaxCount(building.name):
            return False
        
        # Place the building on the world
        for i in range(building.height):
            for j in range(building.width):
                self.world[y + i, x + j] = buildingId
        
        # Add the building to the placedBuildings dictionary
        self.placedBuildings[buildingId] = (building, Position(y, x))
        if building.name not in self.buildingCount:
            self.buildingCount[building.name] = 1
        else:
            self.buildingCount[building.name] += 1

        return True
    
    def getBuildingFromPosition(self, y: int, x: int) -> BaseBuilding:
        if self.isTileEmpty(y, x):
            return -1, None, None
        
        for buildingId, (building, position) in self.placedBuildings.items():
            if position.x <= x < position.x + building.width and position.y <= y < position.y + building.height:
                return buildingId, building, position
            
        return -1, None, None

    def removeBuilding(self, buildingId: int) -> bool:
        if buildingId not in self.placedBuildings:
            return False
        
        building, position = self.placedBuildings[buildingId]
        y, x = position.y, position.x

        # Remove the building from the world
        for i in range(building.height):
            for j in range(building.width):
                self.world[y + i, x + j] = -1
        
        # Remove the building from the placedBuildings dictionary
        del self.placedBuildings[buildingId]
        self.buildingCount[building.name] -= 1
        return True
    
    def getEmptyTileMask(self):
        return self.world == -1
    
    def getBuildingIdGrid(self):
        return self.world

    def getBuildingTypeGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the type of building
            No Building: 0
            Defense: 1
            Resource: 2
            Wall: 3
            TownHall: 4
            Other: 5
        """
        buildingTypeGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    buildingTypeGrid[y + i, x + j] = building.type

        return buildingTypeGrid
    
    def getBuildingLevelGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the level of the building
        """
        buildingLevelGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    buildingLevelGrid[y + i, x + j] = building.level

        return buildingLevelGrid
    
    def getBuildingHpGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the hp of the building
        """
        buildingHpGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    buildingHpGrid[y + i, x + j] = building.getRemHp() * SCALE_FACTOR

        return buildingHpGrid    

    def getBuildingObjectIdentifierGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the generic id of the building
        """
        buildingObjectIdentifier = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    buildingObjectIdentifier[y + i, x + j] = building.id

        return buildingObjectIdentifier

    def getGoldGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the gold stored in the building
        """
        goldGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_RESOURCE:
                        goldGrid[y + i, x + j] = building.getGold()

        return goldGrid
    
    def getElixirGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the elixir stored in the building
        """
        elixirGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_RESOURCE:
                        elixirGrid[y + i, x + j] = building.getElixir()

        return elixirGrid
    
    def getMinAttackRangeGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the min attack range attribute of the building
        """
        attackRangeGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_DEFENSE:
                        attackRangeGrid[y + i, x + j] = building.getMinRange() * SCALE_FACTOR

        return attackRangeGrid
    
    def getMaxAttackRangeGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the max attack range attribute of the building
        """
        attackRangeGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_DEFENSE:
                        attackRangeGrid[y + i, x + j] = building.getMaxRange() * SCALE_FACTOR

        return attackRangeGrid
    
    def getBuildingDphGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the DPH attribute of the building
        """
        damageGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_DEFENSE:
                        damageGrid[y + i, x + j] = building.getDph() * SCALE_FACTOR

        return damageGrid
    
    def getAtkSpeedGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the Attack Speed attribute of the building
        """
        damageGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            assert isinstance(building, BaseBuilding)
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_DEFENSE:
                        damageGrid[y + i, x + j] = building.getAtkSpeed() * SCALE_FACTOR 

        return damageGrid

    def getTargetDomainGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the masked attributes of the building
            Attribute = Air: 2, Ground: 1, Both: 3
        """
        targetDomainGrid = np.zeros((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int)
        for buildingId, (building, position) in self.placedBuildings.items():
            y, x = position.y, position.x
            for i in range(building.height):
                for j in range(building.width):
                    if building.type == BaseBuilding.TYPE_DEFENSE:
                        targetDomainGrid[y + i, x + j] = building.getTargetDomain()

        return targetDomainGrid
    
    def getTargetTroopIDGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the primary key of the target building
        """
        troopIDs = np.ones((self.HEIGHT_WORLD, self.WIDTH_WORLD), dtype=int) * -1
        return troopIDs
    
    def getStepsSinceLastShootGrid(self):
        """
        Returns a grid of the same shape as the world, where each cell contains the initial value of the attribute `steps_since_last_shoot`
        """
        mask = self.getBuildingTypeGrid() == BaseBuilding.TYPE_DEFENSE
        return mask * MILISECONDS_PER_FRAME

    @staticmethod
    def getChannelName(channelNo: int):
        if channelNo == 0:
            return "Building ID"
        elif channelNo == 1:
            return "Building Type"
        elif channelNo == 2:
            return "Building Level"
        elif channelNo == 3:
            return "Building HP"
        elif channelNo == 4:
            return "Gold"
        elif channelNo == 5:
            return "Elixir"
        elif channelNo == 6:
            return "Object Identifier"
        elif channelNo == 7:
            return "Allowed Position"
        elif channelNo == 8:
            return "Min Attack Range"
        elif channelNo == 9:
            return "Max Attack Range"
        elif channelNo == 10:
            return "Building Dph"
        elif channelNo == 11:
            return "Attack Speed"
        elif channelNo == 12:
            return "Target Domain"
        elif channelNo == 13:
            return "Target Troop ID"
        elif channelNo == 14:
            return "Steps Since Last Shoot"
        else:
            return "Unknown"

    def getStateSpace(self):
        return np.stack([
            self.getBuildingIdGrid(),
            self.getBuildingTypeGrid(),
            self.getBuildingLevelGrid(),
            self.getBuildingHpGrid(),
            self.getGoldGrid(),
            self.getElixirGrid(),
            self.getBuildingObjectIdentifierGrid(),
            self.getEmptyTileMask(),
            self.getMinAttackRangeGrid(),
            self.getMaxAttackRangeGrid(),
            self.getBuildingDphGrid(),
            self.getAtkSpeedGrid(),
            self.getTargetDomainGrid(),
            self.getTargetTroopIDGrid(),
            self.getStepsSinceLastShootGrid()
        ], axis=2)
    
    def fillRandomly(self):
        for name, level in self.getAvailableBuidlings():
            for i in range(self.getBuildingMaxCount(name)):
                building = self.getBuildingObject(name)
                for i in range(10):
                    y = random.randint(self.PADDING_WORLD, self.HEIGHT_WORLD - self.PADDING_WORLD - building.height)
                    x = random.randint(self.PADDING_WORLD, self.WIDTH_WORLD - self.PADDING_WORLD - building.width)
                    if self.placeBuilding(building, y, x):
                        break

    # Getters for BaseSpace
    @staticmethod
    def get_building_location(baseState, buildingID):
        return np.where(baseState[:, :, Base.GRID_MAPPING["buildingID"]] == buildingID)
    
    @staticmethod
    def building_reset_target(baseState, buildingID):
        ys, xs = Base.get_building_location(baseState, buildingID)
        baseState[ys, xs, Base.GRID_MAPPING["target_troop_id"]] = -1     

    @staticmethod
    def building_troop_associated_reset_target(baseState: np.ndarray, troopID: int):
        mask = baseState[:, :, Base.GRID_MAPPING["target_troop_id"]] == troopID
        positions = np.where(mask)
        baseState[positions[0], positions[1], Base.GRID_MAPPING["target_troop_id"]] = -1

    @staticmethod
    def get_building_property(baseState, buildingID: int, prop: str):
        assert prop in Base.GRID_MAPPING.keys()
        positions = Base.get_building_location(baseState, buildingID)
        y, x = positions[0][0], positions[1][0]
        return baseState[y, x, Base.GRID_MAPPING[prop]]
    
    @staticmethod
    def building_get_hit(baseState: np.ndarray, buildingID: int, point: float) -> bool:
        locations = Base.get_building_location(baseState, buildingID)
        damage = point
        dead = False
        y_, x_ = locations[0][0], locations[1][0]
        for y, x in zip(locations[0], locations[1]):
            damage = min(point, baseState[y, x, Base.GRID_MAPPING["building_remaining_hp"]])
            baseState[y, x, Base.GRID_MAPPING["building_remaining_hp"]] -= damage
        return baseState[y_, x_, Base.GRID_MAPPING["building_remaining_hp"]]==0, point

    @staticmethod
    def get_undestroyed_building_ids(baseState: np.ndarray) -> np.ndarray:
        mask_undestroyed = baseState[:, :, Base.GRID_MAPPING["building_remaining_hp"]] > 0
        unwall_buildings = baseState[:, :, Base.GRID_MAPPING["building_type"]] != BaseBuilding.TYPE_WALL
        final_mask = np.bitwise_and(mask_undestroyed, unwall_buildings)
        undestroyed_positions = np.where(final_mask)
        return np.unique(baseState[undestroyed_positions[0], undestroyed_positions[1], Base.GRID_MAPPING["buildingID"]])
    
    @staticmethod
    def get_building_target_troop_ID(baseState: np.ndarray, buildingID) -> np.ndarray:
        return Base.get_building_property(baseState, buildingID, "target_troop_id")
    
    @staticmethod
    def building_forget_target(baseState: np.ndarray, positions):
        for y, x in zip(positions[0], positions[1]):
            baseState[y, x, Base.GRID_MAPPING["target_troop_id"]] = -1

    @staticmethod
    def building_attempts_attack(baseState: np.ndarray, troopSpace: np.ndarray, buildingID: int, targetId: int = None, buildingPositions = None) -> bool:
        from .deck import Deck

        # TODO: Debug the attack speed logic

        if targetId is None:
            targetId = Base.get_building_target_troop_ID(baseState, buildingID)
        if targetId == -1:
            return False, 0
        
        dph = Base.get_building_property(baseState, buildingID, "building_dph")
        time_since_last_attack = Base.get_building_property(baseState, buildingID, "steps_since_last_shoot")

        if time_since_last_attack == 0:
            baseState[buildingPositions[0], buildingPositions[1], Base.GRID_MAPPING["steps_since_last_shoot"]] = \
            (time_since_last_attack + MILISECONDS_PER_FRAME) \
                  % Base.get_building_property(baseState, buildingID, "building_atk_speed")
            return Deck.troop_get_hit(troopSpace, targetId, dph)
        
        if buildingPositions is None:
            buildingPositions = Base.get_building_location(baseState, buildingID)

        baseState[buildingPositions[0], buildingPositions[1], Base.GRID_MAPPING["steps_since_last_shoot"]] = \
            (time_since_last_attack + MILISECONDS_PER_FRAME) \
                  % Base.get_building_property(baseState, buildingID, "building_atk_speed")
        
        return False, 0
    
    @staticmethod
    def get_preference_mask(baseState: np.ndarray, preferences: List[int]) -> np.ndarray:
        mask = np.zeros_like(baseState[:, :, 0], dtype=bool)  # Ensure mask is a boolean array
        for preference in preferences:
            mask |= (baseState[:, :, Base.GRID_MAPPING["building_type"]] == preference)  # Bitwise OR with boolean mask

        mask &= (baseState[:, :, Base.GRID_MAPPING["building_remaining_hp"]] > 0)  # Filter out destroyed buildings
        return mask

    @staticmethod
    def get_buildingID_for_position(baseState: np.ndarray, position: Tuple[int, int]) -> int:
        return baseState[position[0], position[1], Base.GRID_MAPPING["buildingID"]]
    
    @staticmethod
    def get_building_type_for_position(baseState: np.ndarray, position: Tuple[int, int]) -> int:
        return baseState[position[0], position[1], Base.GRID_MAPPING["building_type"]]
    
    @staticmethod
    def get_passable_mask(baseState: np.ndarray, isFlying: bool) -> np.ndarray:
        mask = np.ones_like(baseState[:, :, 0])
        if not isFlying:
            mask = np.bitwise_and(mask, baseState[:, :, Base.GRID_MAPPING["building_type"]] != BaseBuilding.TYPE_WALL)
            mask = np.bitwise_or(mask, baseState[:, :, Base.GRID_MAPPING["building_remaining_hp"]] <= 0)
        return mask
    
    @staticmethod
    def loot_building(baseState: np.ndarray,
                      buildingID: int,
                      loot_amount: int,
                      elixir: bool = False,
                      gold: bool = False
        ) -> bool:
        pass

    def __str__(self):
        return str(self.world)
    
    def __repr__(self):
        return str(self.world)

if __name__ == "__main__":
    base = Base(5)
    base.fillRandomly()
    space = base.getStateSpace()

    print(Base.get_building_location(space, 0))
    # print(Base.get_building_property(space, 0, "buildingID"))
    # print(Base.get_undestroyed_building_ids(space))
    # Plot each channel
    fig, axs = plt.subplots(3, 4, figsize=(13, 8))
    fig.suptitle("Base State Space")

    for i in range(3):
        for j in range(4):
            # Show the Heatmap
            channelNo = i * 4 + j
            axs[i, j].imshow(space[:, :, channelNo], cmap="hot")
            axs[i, j].set_title(f"Channel {channelNo}: {Base.getChannelName(channelNo)}", fontsize=8)
            axs[i, j].axis("off")
            cbar = axs[i, j].figure.colorbar(axs[i, j].imshow(space[:, :, channelNo], cmap="hot"), ax=axs[i, j])
            cbar.set_label("Value", fontsize=8)

    fig.tight_layout()
    plt.show()

