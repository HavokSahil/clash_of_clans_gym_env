from warbase import *
from deck import *
from troops import *
import heapq
import numpy as np

BASE_WIDTH = 45
BASE_HEIGHT = 45
BASE_PADDING = 2

class Warzone:
    def __init__(
            self,
            baseSpace: np.ndarray,
            troopSpace: np.ndarray,
            deckSpace: np.ndarray
        ):

        self.baseSpace = baseSpace
        self.troopSpace = troopSpace
        self.deckSpace = deckSpace
        self.timestep = 0
        self.maxtimestep = 1800 # Each step corresponds to 100ms, Total 180s
        self.paths = dict()
        for troopID in range(self.troopSpace.shape[0]):
            self.paths[troopID] = []

        self.destroyed_building_hp = 0
        self.destroyed_buildings_count = 0

        self.elixir_collected = 0
        self.gold_collected = 0

        self.total_hp_map = {}

        self.populate_total_hp_buildings()

        self.total_hp = sum(list(self.total_hp_map.values()))

        self.damage_buildings = 0
        self.damage_troops = 0
        self.troops_lost = 0
        self.troops_deployed = 0

        self.building_damage_map = {}

        self.townhall_building_id = -1
        self.townhall_destroyed = False

        self.destruction_percentage = 0.0

        self.get_town_hall_buildingID()

        self.stars = 0

        # Reward factors
        self.stars_earned_in_move = 0
        self.cumulative_damage_in_move = 0
        self.destruction_percentage_earned_in_move = 0
        self.destroyed_building_count_increment_in_move = 0
        self.troops_lost_in_move = 0
        self.troops_damage_in_move = 0
        self.made_invalid_action_in_move = False


    def populate_total_hp_buildings(self) -> None:
        wall_mask = self.baseSpace[:, :, Base.GRID_MAPPING["building_type"]] != BaseBuilding.TYPE_WALL
        destructable_mask = self.baseSpace[:, :, Base.GRID_MAPPING["building_remaining_hp"]] > 0
        buildingID_grid = self.baseSpace[:, :, Base.GRID_MAPPING["buildingID"]]
        final_mask = np.bitwise_and(wall_mask, destructable_mask)

        rem_hp_grid = self.baseSpace[:, :, Base.GRID_MAPPING["building_remaining_hp"]]
        for i in range(rem_hp_grid.shape[0]):
            for j in range(rem_hp_grid.shape[1]):
                buildingID = buildingID_grid[i][j]
                if final_mask[i][j]:
                    self.total_hp_map[buildingID] = rem_hp_grid[i][j]

    def get_reward(self) -> float:
        reward = self.stars_earned_in_move * 1000000 \
            + self.destruction_percentage_earned_in_move * 10 \
            + self.destroyed_buildings_count + 10 \
            + self.troops_damage_in_move * (-10) \
            + self.troops_lost_in_move * (-100) \
            + self.made_invalid_action_in_move * (-100000000)
        
        return reward

    def get_town_hall_buildingID(self):
        for y in range(self.baseSpace.shape[0]):
            for x in range(self.baseSpace.shape[1]):
                if self.baseSpace[y, x, Base.GRID_MAPPING["building_type"]] == BaseBuilding.TYPE_TOWNHALL:
                    self.townhall_building_id = self.baseSpace[y, x, Base.GRID_MAPPING["buildingID"]]
                    return

    def update(self):

        prev_stars = self.stars
        prev_cum_damage = self.damage_buildings
        prev_destruction_percentage = self.destruction_percentage
        prev_destroyed_building_count = self.destroyed_buildings_count
        prev_troop_lost_count = self.troops_lost
        prev_troop_damage = self.damage_troops
        
        self.update_troop()
        self.update_buildings()

        self.destruction_percentage = self.destroyed_building_hp * 100 / self.total_hp

        self.stars = 0
        if self.destruction_percentage >= 50:
            self.stars += 1
        if self.townhall_destroyed:
            self.stars += 1
        if self.destruction_percentage >= 100:
            self.stars += 1

        self.stars_earned_in_move = self.stars - prev_stars
        self.cumulative_damage_in_move = self.damage_buildings - prev_cum_damage
        self.destruction_percentage_earned_in_move = self.destruction_percentage - prev_destruction_percentage
        self.destroyed_building_count_increment_in_move = self.destroyed_buildings_count - prev_destroyed_building_count
        self.troops_lost_in_move = self.troops_lost - prev_troop_lost_count
        self.troops_damage_in_move = self.damage_troops - prev_troop_damage

    def did_end(self) -> bool:
        #   - Check if the game ends based on following conditions
        #       + If the timestep >= maxtimestep
        flag1 = self.timestep >= self.maxtimestep
        #       + If deck is empty and there is no troop alive
        flag2 = len(Deck.get_deck_available_deploy_options(self.deckSpace)) + len(Deck.get_troops_alive_ids(self.deckSpace)) == 0
        #       + If abort early(hit surrender)
        #       + All non-wall buildings are destroyed
        flag3 = len(Base.get_undestroyed_building_ids(self.baseSpace)) == 0
        
        return flag1 or flag2 or flag3

    def reassign_target_to_single_troop(self, troopID):
        # Get troop's target preference
        targetType = Deck.get_troop_target_preference(self.troopSpace, troopID)
        preferences = TroopDirectory.mapPreferenceToBuildingType(targetType)

        # Get the preference mask for the base
        preference_mask = Base.get_preference_mask(self.baseSpace, preferences)
        # Early exit if no valid targets
        if not np.any(preference_mask):
            # Fallback to general preference
            targetType = TroopBase.PREFER_GENERAL
            preferences = TroopDirectory.mapPreferenceToBuildingType(targetType)
            preference_mask = Base.get_preference_mask(self.baseSpace, preferences)

            if not np.any(preference_mask):  # Still no targets
                return

        # Get target positions as (y, x) pairs
        positions = np.argwhere(preference_mask)

        # Get the troop's current position
        troopPosition = np.array(Deck.get_troop_pos(self.troopSpace, troopID, unscaled=True))

        # Compute distances efficiently using NumPy broadcasting
        distances = np.linalg.norm(positions - troopPosition, axis=1)

        # Find the closest target
        closest_idx = np.argmin(distances)
        closest_position = tuple(positions[closest_idx])

        # Assign target to troop
        targetID = Base.get_buildingID_for_position(self.baseSpace, closest_position)
        Deck.troop_assign_target(self.troopSpace, troopID, targetID)


    def reassign_target_to_all_troops(self):
        troopIDs = Deck.get_troops_alive_ids(self.troopSpace)
        #   - Find nearest target for each troop
        #   - based on preference masking and assign it to them
        for troopID in troopIDs:
            self.reassign_target_to_single_troop(troopID)


    def _helper_get_tile_neighbour(self, tile) -> List[Tuple[int, int]]:
        poss_dels = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (-1, -1), (-1, 1), (1, -1)
        ]

        return [(tile[0] + dely, tile[1] + delx) for dely, delx in poss_dels if 
                (0 <= tile[0] + dely < BASE_HEIGHT) and
                (0 <= tile[1] + delx < BASE_WIDTH)
        ]


    @staticmethod
    def heuristic(pos: Tuple[float, float], goal: Tuple[float, float], D=1, D2=np.sqrt(2)):
        """ Octile distance heuristic function """
        dx = abs(pos[0] - goal[0])
        dy = abs(pos[1] - goal[1])
        return D * max(dx, dy) + (D2 - D) * min(dx, dy)
    

    def find_path_target_building(self, troopID: int):
        start = Deck.get_troop_pos(self.troopSpace, troopID, unscaled=True)
        targetID = Deck.get_troop_target_building(self.troopSpace, troopID)
        targetPositions = Base.get_building_location(self.baseSpace, targetID)
        goal = min(zip(targetPositions[0], targetPositions[1]),
                              key = lambda pos: np.sqrt(pow(pos[0] - start[0], 2) + pow(pos[1] - start[1], 2)))
        
        troopRange = Deck.get_troop_range(self.troopSpace, troopID, unscaled=True)
        isFlying = Deck.get_troop_is_flying(self.troopSpace, troopID)

        start_y, start_x = int(start[0]), int(start[1])
        open_set = [(0, (start_y, start_x))]
        came_from = {}
        g_score = { (start_y, start_x): 0 }
        f_score = { (start_y, start_x): self.heuristic(start, goal) }

        min_heuristic = float('inf')
        passable_mask = Base.get_passable_mask(self.baseSpace, isFlying)
        closest_barrier = None
        aux_goal = None

        if troopID in self.paths:
            self.paths[troopID].clear()

        def goal_test(pos: Tuple[float, float]) -> bool:
            dist = np.sqrt(pow(pos[0] - goal[0], 2) + pow(pos[1] - goal[1], 2))
            return dist <= troopRange
        
        def is_passable(pos: Tuple[float, float]) -> bool:
            y, x = int(pos[0]), int(pos[1])
            return passable_mask[y, x]

        while open_set:
            _, pos = heapq.heappop(open_set)
            if goal_test(pos):
                aux_goal = pos
                break

            for neib in self._helper_get_tile_neighbour(pos):
                cost = g_score[pos] + 1
                f = cost + self.heuristic(neib, goal)

                if f < min_heuristic and not is_passable(neib):
                    min_heuristic = f
                    closest_barrier = neib
                    came_from[neib] = pos

                if is_passable(neib) and (neib not in g_score or cost < g_score[neib]):
                    g_score[neib] = cost
                    f_score[neib] = f
                    heapq.heappush(open_set, (f, neib))
                    came_from[neib] = pos

        if aux_goal not in came_from:
            # If the goal is not reached
            if closest_barrier is None or closest_barrier not in came_from:
                return False
            
            buildingID = Base.get_buildingID_for_position(self.baseSpace, closest_barrier)
            buildingType = Base.get_building_type_for_position(self.baseSpace, closest_barrier)
            # Just for debug, ensure that the barrier building is wall
            assert(buildingType == BaseBuilding.TYPE_WALL)

            Deck.troop_assign_target(self.troopSpace, troopID, buildingID)

            current = closest_barrier
            while current != (start_y, start_x):
                self.paths[troopID].append(current)
                current = came_from[current]
            return True
        
        # Reconstruct the path to the reachable cell if the goal is in range
        current = aux_goal
        while current != (start_y, start_x):
            self.paths[troopID].append(current)
            current = came_from[current]
        return True

        #   - Performed a ranged A* search on the mask
        #   - If the path is found: store the path, return True
        #   - If the path is not found, then return false,
        #   - Perform a ranged A* and store the closest approach
        #       to the target, store the barrier that could have
        #       improved the heuristic function as new target,
        #   - Update the path based on the new target


    def deploy_troop(self, deckID: int, position: Tuple[int, int]) -> bool:
        # Perform the deploy action given by the gym environment update
        self.made_invalid_action_in_move = False
        if 0 <= deckID < len(self.deckSpace[:, 0]):
            troopID = Deck.get_available_troopID(self.troopSpace)
            deployed =  Deck.deploy_troop_from_deck(self.deckSpace, self.troopSpace, deckID, troopID, position)
            self.troops_deployed += deployed
            if not deployed: self.made_invalid_action_in_move = True
    
    def _helper_troop_target_in_range(self, troopID):

        troopPos = Deck.get_troop_pos(self.troopSpace, troopID, unscaled=True)
        targetID = Deck.get_troop_target_building(self.troopSpace, troopID)
        troopRange = Deck.get_troop_range(self.troopSpace, troopID, unscaled=True)

        if targetID == -1: return False
        positions = Base.get_building_location(self.baseSpace, targetID)
        for y, x in zip(positions[0], positions[1]):
            if np.sqrt(pow(y-troopPos[0], 2) + pow(x-troopPos[1], 2)) <= troopRange:
                return True
        
        return False

    def update_troop(self):
        ### Troops Update
        #   - Troops with no target should get a target
        targetlessTroop = Deck.get_targetless_troopID(self.troopSpace)

        for troopID in targetlessTroop:
            self.reassign_target_to_single_troop(troopID)
            self.find_path_target_building(troopID)
        #   - Troops with target should move toward target

        for troopID in Deck.get_troops_alive_ids(self.troopSpace):
            troopID = troopID
            if len(self.paths[troopID]) != 0:
                next_pos = self.paths[troopID][-1]
                if Deck.troop_move(self.troopSpace, troopID, next_pos, len(self.paths[troopID]) == 1):
                    self.paths[troopID].pop()
                    return

            if self._helper_troop_target_in_range(troopID):
                buildingID = Deck.get_troop_target_building(self.troopSpace, troopID)
                sacrificial_troop = False
                building_destroyed, damage = Deck.troop_attempts_attack(self.troopSpace, self.baseSpace, troopID)
                isWall = Base.get_building_property(self.baseSpace, Deck.get_troop_target_building(self.troopSpace, troopID), "building_type") == BaseBuilding.TYPE_WALL

                # Handle wall breaker
                if Deck.get_troop_target_preference(self.troopSpace, troopID) == TroopBase.PREFER_WALL and damage > 0:
                    # Kill the wall breaker
                    self.troops_lost += 1
                    remHp = Deck.get_troop_hp(self.troopSpace, troopID)
                    dead, point = Deck.troop_get_hit(self.troopSpace, troopID, remHp * 1000)
                    self.damage_troops += point

                if not isWall:
                    self.damage_buildings += damage
                    if buildingID not in self.building_damage_map:
                        self.building_damage_map[buildingID] = damage
                    else:
                        self.building_damage_map[buildingID] += damage

                if building_destroyed:
                    if buildingID == self.townhall_building_id:
                        self.townhall_destroyed = True
                    Deck.troops_forget_target_all(self.troopSpace)
                    if not isWall:
                        self.destroyed_building_hp += self.total_hp_map[buildingID]
                        self.destroyed_buildings_count += 1
                    return
                
 
    # Methods concerning buildings

    def find_troop_in_range(self, positions) -> bool:
        # TODO: Test this method
        y, x = positions[0][0], positions[1][0]
        centroid_y, centroid_x = int(np.mean(positions[0])), int(np.mean(positions[1]))
        buildingMinRange = self.baseSpace[y, x, Base.GRID_MAPPING["building_min_atk_range"]] / SCALE_FACTOR
        buildingMaxRange = self.baseSpace[y, x, Base.GRID_MAPPING["building_max_atk_range"]] / SCALE_FACTOR

        domain = self.baseSpace[y, x, Base.GRID_MAPPING["building_target_domain"]]

        hit_air = domain == 3 or domain == 2
        hit_ground = domain == 3 or domain == 1

        aliveTroopIDs = Deck.get_troops_alive_ids(self.troopSpace)
        for troopID in aliveTroopIDs:
            is_flying = Deck.get_troop_is_flying(self.troopSpace, troopID)

            if is_flying and not hit_air:
                continue

            if not is_flying and not hit_ground:
                continue

            target_y, target_x = Deck.get_troop_pos(self.troopSpace, troopID, unscaled=True)
            if buildingMinRange <= np.sqrt(pow(target_y - centroid_y, 2) + pow(target_x - centroid_x, 2)) <= buildingMaxRange:
                for y, x in zip(positions[0], positions[1]):
                    self.baseSpace[y, x, Base.GRID_MAPPING["target_troop_id"]] = troopID
                return True
            
        return False
    
    def is_target_troop_in_range(self, positions, targetID: int):
        # TODO: Test this method
        y, x = positions[0][0], positions[1][0]
        centroid_y, centroid_x = int(np.mean(positions[0])), int(np.mean(positions[1]),)
        target_y, target_x = Deck.get_troop_pos(self.troopSpace, targetID, unscaled=True)
        buildingMinRange = self.baseSpace[y, x, Base.GRID_MAPPING["building_min_atk_range"]] / SCALE_FACTOR
        buildingMaxRange = self.baseSpace[y, x, Base.GRID_MAPPING["building_max_atk_range"]] / SCALE_FACTOR
        return buildingMinRange <= np.sqrt(pow(centroid_y - target_y, 2) + pow(centroid_x - target_x, 2)) <= buildingMaxRange


    def building_attack_troop_target(self, buildingID: int, targetID: int, positions) -> bool:
        # TODO: Test this method
        return Base.building_attempts_attack(self.baseSpace, self.troopSpace, buildingID, targetID, positions)
        #   - If the target is in range
        #       if the steps since last attack is 0
        #           then hit the target
        #       If the target dies, reset the target of all those buildings,
        #           that were hitting the destroyed troop
        #       else
        #           make modular increment to the steps,

    def update_defense_buildings(self, buildingID: int):
        # TODO: To test this method
        ### Buildings Update
        positions = Base.get_building_location(self.baseSpace, buildingID)
        targetID = Base.get_building_target_troop_ID(self.baseSpace, buildingID)
        if targetID != -1 and \
            self.is_target_troop_in_range(positions, targetID) and \
            Deck.get_troop_hp(self.troopSpace, targetID) > 0:
            target_dead, damage = self.building_attack_troop_target(buildingID, targetID, positions)
            if target_dead:
                Base.building_forget_target(self.baseSpace, positions)
                self.troops_lost += 1
            self.damage_troops += damage
            return

        self.find_troop_in_range(positions)

    def update_buildings(self):
        buildingTypeMask = np.bitwise_and(
            self.baseSpace[:, :, Base.GRID_MAPPING["building_type"]],
            self.baseSpace[:, :, Base.GRID_MAPPING["building_remaining_hp"]] > 0
        )
        done_building = set()
        for y, x in np.argwhere(buildingTypeMask):
            if buildingTypeMask[y, x] == BaseBuilding.TYPE_DEFENSE:
                buildingID = self.baseSpace[y, x, Base.GRID_MAPPING["buildingID"]]
                if buildingID not in done_building:
                    self.update_defense_buildings(buildingID)
                    done_building.add(buildingID)
