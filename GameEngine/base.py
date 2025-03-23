from .structures import *
from .troops import *
import numpy as np

class SceneBase:

    BASE_HEIGHT     = 45
    BASE_WIDTH      = 45
    BASE_PADDING    = 2

    BASE_ORIGIN     = (0, 0)
    BASE_CENTER     = (22, 22)
    BASE_CORNER     = (44, 44)

    def __init__(self):
        self.map = np.empty((SceneBase.BASE_HEIGHT, SceneBase.BASE_WIDTH), dtype=object)
        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):
                self.map[y, x] = {"building": None, "troops": set()}

        self.building_positions = {}  # Maps building -> [(x, y), ...]
        self.troop_positions = {}     # Maps troop -> (x, y)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.BASE_WIDTH and 0 <= y < self.BASE_HEIGHT

    def is_tile_empty(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.map[y, x] is None

    def place_building(self, building: BaseStructure, x, y):

        width = building.width
        height = building.height

        if not self.can_place_building(x, y, width, height):
            return False

        for dy in range(height):
            for dx in range(width):
                self.map[y + dy, x + dx]["building"] = building
        self.building_positions[building] = [(x + dx, y + dy) for dy in range(height) for dx in range(width)]
        building.x, building.y = x, y
        return True

    def can_place_building(self, x, y, width, height):
        for dy in range(height):
            for dx in range(width):
                if not self.in_bounds(x + dx, y + dy):
                    return False
                if self.map[y + dy, x + dx]["building"] is not None:
                    return False
        return True

    def place_troop(self, troop: TroopBase, x: int, y: int):
        if not self.in_bounds(x, y):
            return False
        self.map[y, x]["troops"].add(troop)
        self.troop_positions[troop] = (x, y)
        troop.x, troop.y = x, y
        return True

    def remove_building(self, building: BaseStructure):
        if building not in self.building_positions:
            return
        for x, y in self.building_positions[building]:
            self.map[y, x]["building"] = None
        del self.building_positions[building]

    def remove_troop(self, troop: TroopBase):
        if troop not in self.troop_positions:
            return
        x, y = self.troop_positions[troop]
        self.map[y, x]["troops"].discard(troop)
        del self.troop_positions[troop]