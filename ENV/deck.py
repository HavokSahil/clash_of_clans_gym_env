import numpy as np
import random
from troops import *
from typing import List, Tuple
import matplotlib.pyplot as plt


class Deck:

    DECK_MAPPING = {
        "deckID": 0,
        "count": 1,
        "hp": 2,
        "dph": 3,
        "mov_speed": 4,
        "atk_speed": 5,
        "range": 6,
        "is_flying": 7,
        "target_preference": 8,
        "target_domain": 9
    }

    TROOP_MAPPING = {
        "troopID": 0,
        "pos_y": 1,
        "pos_x": 2,
        "steps_since_last_move": 3,
        "steps_since_last_hit": 4, 
        "mov_speed": 5,
        "atk_speed": 6,
        "is_flying": 7,
        "target_domain": 8,
        "hp": 9,
        "dph": 10,
        "range": 11,
        "target_preference": 12,
        "target_building": 13,
        "deck_id": 14,
    }

    CAMP_CAPACITY_MAP = {
        # Townhall 1
        1: 20,
        # Townhall 2
        2: 30,
        # Townhall 3
        3: 70,
        # Townhall 4
        4: 80,
        # Townhall 5
        5: 135,
    }

    HOUSING_SPACE_MAP = {
        "Barbarian": 1,
        "Archer": 1,
        "Giant": 5,
        "Goblin": 1,
        "Wall Breaker": 2,
        "Balloon": 5,
        "Wizard": 4,
    }

    DECK_ID_MAPS_NAME = {
        0: "Barbarian",
        1: "Archer",
        2: "Giant",
        3: "Goblin",
        4: "Wall Breaker",
        5: "Balloon",
        6: "Wizard",
    }

    def __init__(self, townHallLevel: int = 1):
        self.deck = {
            "Barbarian": 0,
            "Archer": 0,
            "Giant": 0,
            "Goblin": 0,
            "Wall Breaker": 0,
            "Balloon": 0,
            "Wizard": 0,
        }

        self.townHallLevel = townHallLevel
        self.troopDirectory = TroopDirectory(self.townHallLevel)
        self.capacity = self.CAMP_CAPACITY_MAP[self.townHallLevel]
        self.occupancy = 0

    def clear(self):
        self.resetDeck()

    def getHousingSpace(self, name: str) -> int:
        if name in self.HOUSING_SPACE_MAP:
            return self.HOUSING_SPACE_MAP[name]
        else:
            return 1000000

    def getTroopLevel(self, name: str) -> int:
        return self.troopDirectory.getTroopLevel(name)

    def getAllTroops(self) -> List[str]:
        return list(self.deck.keys())

    def getTroopCategoryIndex(self, name: str) -> int:
        return self.troopDirectory.getTroopCategoryIndex(name)

    def availableSpace(self) -> int:
        return self.capacity - self.occupancy
    
    def getAvailableTroops(self) -> List[Tuple[str, int]]:
        availableTroops = []
        for name in self.troopDirectory.getAllTroopNames():
            if self.getHousingSpace(name) <= self.availableSpace():
                availableTroops.append((name, self.troopDirectory.getTroopLevel(name)))    

        return availableTroops
    
    def getTroopCount(self, name) -> int:
        return self.deck.get(name, 0)
    
    def totalTroopCount(self) -> int:
        return sum(self.deck.values())

    def canRecruitTroop(self, name) -> bool:
        return self.getHousingSpace(name) <= self.availableSpace()

    def isTroopAvailable(self, name) -> bool:
        return self.getTroopCount(name) > 0

    def recruitTroop(self, name):
        if self.canRecruitTroop(name):
            self.deck[name] = self.getTroopCount(name) + 1
            self.occupancy += self.getHousingSpace(name)
            return True
        else:
            return False
        
    def disbandTroop(self, name):
        if self.isTroopAvailable(name):
            self.deck[name] = self.getTroopCount(name) - 1
            self.occupancy -= self.getHousingSpace(name)
            return True
        else:
            return False

    def resetDeck(self):
        self.deck.clear()
        self.occupancy = 0

    def fillRandomly(self):
        self.resetDeck()
        availableTroops = self.getAvailableTroops()
        for i in range(self.capacity):
            if len(availableTroops) == 0:
                break
            name, level = random.choice(availableTroops)
            self.recruitTroop(name)
            availableTroops = self.getAvailableTroops()

    def getCountVector(self) -> np.ndarray:
        countVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            countVector[self.getTroopCategoryIndex(name)] = count
        return countVector
    
    def getHpVector(self) -> np.ndarray:
        hpVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            hpVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getHP() * SCALE_FACTOR
        return hpVector
    
    def getDphVector(self) -> np.ndarray:
        dphVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            dphVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getDph() * SCALE_FACTOR
        return dphVector
    
    def getRemHpVector(self) -> np.ndarray:
        remHpVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            remHpVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getRemHP() * SCALE_FACTOR
        return remHpVector
    
    def getMovSpeedVector(self) -> np.ndarray:
        movSpeedVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            movSpeedVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getMovSpeed() * SCALE_FACTOR
        return movSpeedVector
    
    def getAtkSpeedVector(self) -> np.ndarray:
        atkSpeedVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            atkSpeedVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getAtkSpeed() * SCALE_FACTOR 
        return atkSpeedVector
    
    def getAtkRangeVector(self) -> np.ndarray:
        atkRangeVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            atkRangeVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getAtkRange() * SCALE_FACTOR
        return atkRangeVector

    def getFlyingVector(self) -> np.ndarray:
        flyingVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            flyingVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).canFly()
        return flyingVector
    
    def getTargetPreferenceVector(self) -> np.ndarray:
        targetPreferenceVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            targetPreferenceVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getPreference()
        return targetPreferenceVector
    
    def getTargetDomainVector(self) -> np.ndarray:
        """
        Target Domain: (01): Ground | (10): Air | (11): Both
        """
        targetDomainVector = np.zeros(len(self.troopDirectory.getAllTroopNames()), dtype=int)
        for name, count in self.deck.items():
            targetDomainVector[self.getTroopCategoryIndex(name)] = self.troopDirectory.getTroopObject(name).getTargetDomain()
        return targetDomainVector
    
    def getUnplacedTroopSpace(self) -> np.ndarray:
        troopSpace = np.ones(shape=(self.capacity, len(self.TROOP_MAPPING.keys())), dtype=int) * -1
        return troopSpace
    
    def getStateSpace(self) -> np.ndarray:
        return np.stack([
            np.arange(len(self.getCountVector())),  
            self.getCountVector(),                  
            self.getHpVector(),                     
            self.getDphVector(),                    
            self.getMovSpeedVector(),               
            self.getAtkSpeedVector(),               
            self.getAtkRangeVector(),               
            self.getFlyingVector(),                 
            self.getTargetPreferenceVector(),       
            self.getTargetDomainVector()            
        ], axis=1)

    # Getters for DeckSpace
    @staticmethod
    def get_deck_member_ids(deckSpace: np.ndarray):
        return np.unique(deckSpace[:, Deck.DECK_MAPPING["deckID"]])
    
    @staticmethod
    def get_deck_member_count(deckSpace: np.ndarray, member_id: int) -> int:
        return deckSpace[member_id, Deck.DECK_MAPPING["count"]]
    
    @staticmethod
    def get_deck_member_hp(deckSpace: np.ndarray, member_id: int) -> float:
        return deckSpace[member_id, Deck.DECK_MAPPING["hp"]]
    
    @staticmethod
    def get_deck_member_dph(deckSpace: np.ndarray, member_id: int) -> float:
        return deckSpace[member_id, Deck.DECK_MAPPING["dph"]]

    @staticmethod
    def get_deck_member_mov_speed(deckSpace: np.ndarray, member_id: int) -> float:
        return deckSpace[member_id, Deck.DECK_MAPPING["mov_speed"]]

    @staticmethod
    def get_deck_member_atk_speed(deckSpace: np.ndarray, member_id: int) -> float:
        return deckSpace[member_id, Deck.DECK_MAPPING["atk_speed"]]
    
    def get_deck_member_range(deckSpace: np.ndarray, member_id: int) -> float:
        return deckSpace[member_id, Deck.DECK_MAPPING["range"]]

    @staticmethod
    def get_deck_member_is_flying(deckSpace: np.ndarray, member_id: int) -> bool:
        return deckSpace[member_id, Deck.DECK_MAPPING["is_flying"]]

    @staticmethod
    def get_deck_member_target_preference(deckSpace: np.ndarray, member_id: int) -> int:
        return deckSpace[member_id, Deck.DECK_MAPPING["target_preference"]]

    @staticmethod
    def get_deck_member_target_domain(deckSpace: np.ndarray, member_id: int) -> int:
        return deckSpace[member_id, Deck.DECK_MAPPING["target_domain"]]

    
    # Getters for TroopSpace
    @staticmethod
    def get_troop_ids(troopSpace: np.ndarray) -> np.ndarray:
        troop_ids_index = np.where(troopSpace[:, Deck.TROOP_MAPPING["troopID"]] != -1)[0]
        troop_ids = np.unique(troopSpace[troop_ids_index, Deck.TROOP_MAPPING["troopID"]])
        return troop_ids
    
    @staticmethod
    def get_troop_pos(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> Tuple[float, float]:
        y = troopSpace[troopID, Deck.TROOP_MAPPING["pos_y"]]
        x = troopSpace[troopID, Deck.TROOP_MAPPING["pos_x"]]
        if (y == -1) or (x == -1): return (-1, -1)
        return (y/SCALE_FACTOR, x/SCALE_FACTOR) if unscaled else (y, x)
    
    @staticmethod
    def get_troop_steps_since_last_move(troopSpace: np.ndarray, troopID: int) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_move"]]
    
    @staticmethod
    def get_troop_steps_since_last_hit(troopSpace: np.ndarray, troopID: int) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_hit"]]
    
    @staticmethod
    def get_troop_mov_speed(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> float:
        return troopSpace[troopID, Deck.TROOP_MAPPING["mov_speed"]] if not unscaled else troopSpace[troopID, Deck.TROOP_MAPPING["mov_speed"]] / SCALE_FACTOR
    
    @staticmethod
    def get_troop_atk_speed(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["atk_speed"]] 

    @staticmethod
    def get_troop_is_flying(troopSpace: np.ndarray, troopID: int) -> bool:
        return troopSpace[troopID, Deck.TROOP_MAPPING["is_flying"]]
    
    @staticmethod
    def get_troop_target_domain(troopSpace: np.ndarray, troopID: int) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["target_domain"]]
    
    @staticmethod
    def get_troop_hp(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> float:
        return troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] if not unscaled else troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] / SCALE_FACTOR
    
    @staticmethod
    def get_troop_dph(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> float:
        return troopSpace[troopID, Deck.TROOP_MAPPING["dph"]] if not unscaled else (troopSpace[troopID, Deck.TROOP_MAPPING["dph"]] / SCALE_FACTOR)
    
    @staticmethod
    def get_troop_range(troopSpace: np.ndarray, troopID: int, unscaled: bool = False) -> float:
        return troopSpace[troopID, Deck.TROOP_MAPPING["range"]] if not unscaled else troopSpace[troopID, Deck.TROOP_MAPPING["range"]] / SCALE_FACTOR
    
    @staticmethod
    def get_troop_target_preference(troopSpace: np.ndarray, troopID: int) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["target_preference"]]

    @staticmethod
    def get_troop_target_building(troopSpace: np.ndarray, troopID: int) -> int:
        return troopSpace[troopID, Deck.TROOP_MAPPING["target_building"]]
    
    # Utility Funtions for Deck
    @staticmethod
    def get_deck_available_deploy_options(deckSpace: np.ndarray) -> np.ndarray:
        non_empty = np.where(deckSpace[:, Deck.DECK_MAPPING["count"]] != 0)[0]
        return deckSpace[non_empty, Deck.DECK_MAPPING["deckID"]]
    
    @staticmethod
    def get_available_troopID(troopSpace: np.ndarray) -> int:
        return np.min(np.where(troopSpace[:, Deck.TROOP_MAPPING["troopID"]] == -1)[0])
    
    @staticmethod
    def deploy_troop_from_deck(
        deckSpace: np.ndarray,
        troopSpace: np.ndarray,
        deckID: int,
        troopID: int,
        pos: Tuple[int, int]
    ) -> bool:
        if not deckSpace[deckID, Deck.DECK_MAPPING["count"]] > 0 and \
            troopSpace[troopID, Deck.TROOP_MAPPING["troopID"]] == -1:
            return False

        deckSpace[deckID, Deck.DECK_MAPPING["count"]] = deckSpace[deckID, Deck.DECK_MAPPING["count"]] - 1
        try:
            troopSpace[troopID, Deck.TROOP_MAPPING["troopID"]] = troopID
            troopSpace[troopID, Deck.TROOP_MAPPING["pos_y"]] = pos[0] * SCALE_FACTOR
            troopSpace[troopID, Deck.TROOP_MAPPING["pos_x"]] = pos[1] * SCALE_FACTOR
            troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_move"]] = MILISECONDS_PER_FRAME
            troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_hit"]] = MILISECONDS_PER_FRAME
            troopSpace[troopID, Deck.TROOP_MAPPING["mov_speed"]] = Deck.get_deck_member_mov_speed(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["atk_speed"]] = Deck.get_deck_member_atk_speed(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["is_flying"]] = Deck.get_deck_member_is_flying(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["target_domain"]] = Deck.get_deck_member_target_domain(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] = Deck.get_deck_member_hp(deckSpace, deckID) 
            troopSpace[troopID, Deck.TROOP_MAPPING["dph"]] = Deck.get_deck_member_dph(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["range"]] = Deck.get_deck_member_range(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["target_preference"]] = Deck.get_deck_member_target_preference(deckSpace, deckID)
            troopSpace[troopID, Deck.TROOP_MAPPING["target_building"]] = -1
            troopSpace[troopID, Deck.TROOP_MAPPING["deck_id"]] = deckID
        except Exception as e:
            print("An error occured", e)
            return False
        finally:
            return True
        
    # TroopSpace Utility Function
    @staticmethod
    def get_troops_alive_ids(troopSpace: np.ndarray):
        troop_exist_mask    = troopSpace[:, Deck.TROOP_MAPPING["troopID"]] != -1
        troop_alive_mask    = troopSpace[:, Deck.TROOP_MAPPING["hp"]] > 0
        final_mask          = np.bitwise_and(troop_alive_mask, troop_exist_mask)
        troop_ids_pos       = np.where(final_mask)[0]
        return troopSpace[troop_ids_pos, Deck.TROOP_MAPPING["troopID"]]
    
    @staticmethod
    def get_targetless_troopID(troopSpace: np.ndarray) -> np.ndarray:
        troop_exist_mask    = troopSpace[:, Deck.TROOP_MAPPING["troopID"]] != -1
        troop_alive_mask    = troopSpace[:, Deck.TROOP_MAPPING["hp"]] > 0
        troop_lost_mask     = troopSpace[:, Deck.TROOP_MAPPING["target_building"]] == -1
        final_mask  = np.bitwise_and(troop_exist_mask, troop_alive_mask)
        final_mask  = np.bitwise_and(final_mask, troop_lost_mask)
        troop_ids   = np.where(final_mask)[0]
        return troopSpace[troop_ids, Deck.TROOP_MAPPING["troopID"]]

    @staticmethod
    def troops_forget_target_all(troopSpace: np.ndarray) -> None:
        troopSpace[:, Deck.TROOP_MAPPING["target_building"]] = -1

    @staticmethod
    def troop_get_hit(troopSpace: np.ndarray, troopID: int, point: float) -> bool:
        """ Reduce the hitpoint of the troop and returns True if it is dead """
        damage = 0
        damage = min(point, troopSpace[troopID, Deck.TROOP_MAPPING["hp"]])
        troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] -= point
        if (troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] <= 0):
            troopSpace[troopID, Deck.TROOP_MAPPING["hp"]] = 0
            return True, damage
        return False, damage
    
    @staticmethod
    def troop_attempts_attack(troopSpace: np.ndarray, baseSpace: np.ndarray, troopID: int, targetID: int = None) -> bool:
        from warbase import Base
        if targetID is None:
            targetID = Deck.get_troop_target_building(troopSpace, troopID)
        if targetID == -1:
            return False, 0
            
        dph = Deck.get_troop_dph(troopSpace, troopID)
        time_since_last_attack = Deck.get_troop_steps_since_last_hit(troopSpace, troopID)

        if time_since_last_attack == 0:
            troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_hit"]] = (time_since_last_attack + MILISECONDS_PER_FRAME) \
            %Deck.get_troop_atk_speed(troopSpace, troopID)
            return Base.building_get_hit(baseSpace, targetID, dph*10)
        
        troopSpace[troopID, Deck.TROOP_MAPPING["steps_since_last_hit"]] = (time_since_last_attack + MILISECONDS_PER_FRAME) \
            %Deck.get_troop_atk_speed(troopSpace, troopID)
        
        return False, 0
    
    @staticmethod
    def troop_assign_target(troopSpace: np.ndarray, troopID: int, buildingID: int):
        """ Assign the building Id to a specific troop in the troop space """
        troopSpace[troopID, Deck.TROOP_MAPPING["target_building"]] = buildingID

    @staticmethod
    def troop_set_pos(troopSpace: np.ndarray, troopID: int, finalPos: Tuple[int, int]):
        y, x = finalPos
        troopSpace[troopID, Deck.TROOP_MAPPING["pos_y"]] = y 
        troopSpace[troopID, Deck.TROOP_MAPPING["pos_x"]] = x

    @staticmethod
    def troop_move(troopSpace: np.ndarray, troopID: int, finalPos: Tuple[int, int], round_final: bool = False) -> bool:
        """ Returns True if the goal is in threshold """
        y_init, x_init  = Deck.get_troop_pos(troopSpace, troopID, unscaled=True)
        y_fnl,  x_fnl   = finalPos[0], finalPos[1]
        D = np.sqrt(pow(y_fnl - y_init, 2) + pow(x_fnl - x_init, 2))
        d = Deck.get_troop_mov_speed(troopSpace, troopID, unscaled=True)
        if d > D:
            if round_final:
                y_fnl = int(y_fnl * SCALE_FACTOR)
                x_fnl = int(x_fnl * SCALE_FACTOR)
                Deck.troop_set_pos(troopSpace, troopID, (y_fnl, x_fnl))
            return True
        
        y_ = int(round(y_init + (y_fnl - y_init) * d/D, 4) * SCALE_FACTOR)
        x_ = int(round(x_init + (x_fnl - x_init) * d/D, 4) * SCALE_FACTOR)

        Deck.troop_set_pos(troopSpace, troopID, (y_, x_))
        return False

    
    def __str__(self):
        return str(self.deck)
    
    def __repr__(self):
        return str(self.deck)
    
if __name__ == "__main__":
    deck = Deck(townHallLevel=5)
    deck.fillRandomly()
    deckSpace = deck.getStateSpace()
    troopSpace = deck.getUnplacedTroopSpace()
    print(deck.get_troop_ids(troopSpace))
    print(deck.get_troop_pos(troopSpace, 1))
    print(deck.get_troop_steps_since_last_hit(troopSpace, 1))
    print(deck.get_troop_steps_since_last_move(troopSpace, 1))
    print(deck.get_troop_is_flying(troopSpace, 1))
    print(deck.get_troop_range(troopSpace, 1))
    print(deck.get_troop_dph(troopSpace, 1))
    print(deck.get_troop_target_preference(troopSpace, 1))
    print(deck.get_troop_target_building(troopSpace, 1))
    print(deck.get_deck_available_deploy_options(deckSpace))
    
    for i in range(135):
        print("Attempt: ", i)
        options = deck.get_deck_available_deploy_options(deckSpace)
        troopID = deck.get_available_troopID(troopSpace)
        if not len(options):
            print("Deck Empty")
            break
        if not deck.deploy_troop_from_deck(deckSpace, troopSpace, options[0], troopID, (2, 2)):
            print("Couldn't deploy troop")
            break

        print("Alive", deck.get_troops_alive_ids(troopSpace))

    # Make a Bar Chart
    fig, ax = plt.subplots()
    ax.bar(deck.troopDirectory.getAllTroopNames(), deck.getCountVector())
    plt.title("Deck State Space")
    plt.show()
