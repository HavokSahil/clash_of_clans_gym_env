import numpy as np
import pygame
import pygame_gui
from troops import *
from deck import Deck
from buildings import BaseBuilding, BuildingDirectory
from warbase import Base

TILE_SIZE = 20
GRID_SIZE = BASE_WIDTH
PADDING = BASE_PADDING

SCENE_PADDING = PADDING * TILE_SIZE
SCENE_WIDTH = GRID_SIZE * TILE_SIZE + SCENE_PADDING
SCENE_HEIGHT = GRID_SIZE * TILE_SIZE + SCENE_PADDING

GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)

class WarzoneRenderer:
    def __init__(self):
        

        pygame.init()
        pygame.display.set_caption('Clash of Clans Warzone')
        self.screen = pygame.display.set_mode((SCENE_WIDTH, SCENE_HEIGHT))

        self.clock = pygame.time.Clock()

        self.image_cache = {}

        self.hovered_building = None
        self.grid_on = False

    def loadImage(self, image_path, width=1, height=1):
        if (image_path, width, height) not in self.image_cache:
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.scale(image, (width * TILE_SIZE, height * TILE_SIZE))
            self.image_cache[(image_path, width, height)] = image
        return self.image_cache[(image_path, width, height)]

    def drawBuilding(self, baseState: np.ndarray, y: int, x: int):

        draw_x = x * TILE_SIZE + SCENE_PADDING
        draw_y = y * TILE_SIZE + SCENE_PADDING

        buildingID = baseState[y, x, Base.GRID_MAPPING["buildingID"]]
        if buildingID == -1: return
        locations = Base.get_building_location(baseState, buildingID)
        top_left_corner = (locations[0][0], locations[1][0])
        if (y, x) != top_left_corner: return
        buildingLevel = baseState[y, x, Base.GRID_MAPPING["building_level"]]
        buildingObjectIdentifier = baseState[y, x, Base.GRID_MAPPING["building_object_identifier"]]
        buildingType = baseState[y, x, Base.GRID_MAPPING["building_type"]]

        buildingObject = BuildingDirectory.getBuildingObjectFromID(buildingObjectIdentifier, buildingLevel)
        maxHp = buildingObject.getHp()
        remainingHp = baseState[y, x, Base.GRID_MAPPING["building_remaining_hp"]] / SCALE_FACTOR

        health = remainingHp / maxHp if maxHp != 0 else 0.0

        if health == 0:
            pygame.draw.line(self.screen, (255, 0, 0), (draw_x, draw_y), (draw_x + TILE_SIZE * buildingObject.width, draw_y + TILE_SIZE * buildingObject.height), 4)
            pygame.draw.line(self.screen, (255, 0, 0), (draw_x + TILE_SIZE * buildingObject.width, draw_y), (draw_x, draw_y + TILE_SIZE * buildingObject.height), 4)
            return

        # Draw the health bar
        if health < 1:
            pygame.draw.rect(self.screen, (255, 0, 0), (draw_x + 4, draw_y - 2, TILE_SIZE * buildingObject.width - 8, 3))
            pygame.draw.rect(self.screen, (0, 255, 0), (draw_x + 4, draw_y - 2, (TILE_SIZE * buildingObject.width - 8) * health, 3))

        img = self.loadImage(buildingObject.getImagePath(), buildingObject.width, buildingObject.height)
        self.screen.blit(img, (draw_x, draw_y))

    def drawTroops(self, troopSpace: np.ndarray, baseSpace: np.ndarray, troopID: int, townhall_level):
        if troopID == -1: return
        deckID = troopSpace[troopID, Deck.TROOP_MAPPING["deck_id"]]
        troopName = Deck.DECK_ID_MAPS_NAME[deckID]
        troop = TroopDirectory.getTroopObjectStatic(troopName, townhall_level)
        maxHp = troop.getHP()
        remainingHp = Deck.get_troop_hp(troopSpace, troopID, unscaled=True)

        targetID = Deck.get_troop_target_building(troopSpace, troopID)
        if targetID != -1:
            locations = Base.get_building_location(baseSpace, targetID)
            target_x = locations[1][0] * TILE_SIZE + SCENE_PADDING
            target_y = locations[0][0] * TILE_SIZE + SCENE_PADDING
            width = int(np.sqrt(len(locations[0])))
            pygame.draw.rect(self.screen, (255, 0, 0), (target_x, target_y, TILE_SIZE * width, TILE_SIZE * width), 2)

        health = remainingHp /  maxHp

        img = self.loadImage(troop.getImagePath())
        img = pygame.transform.scale(img, (TILE_SIZE + 1, TILE_SIZE + 1))

        pos_y, pos_x = Deck.get_troop_pos(troopSpace, troopID, unscaled=True)
        pos_y = pos_y * TILE_SIZE + SCENE_PADDING
        pos_x = pos_x * TILE_SIZE + SCENE_PADDING

        pygame.draw.rect(self.screen, (255, 0, 0), (pos_x, pos_y - 2, TILE_SIZE-2, 3))
        pygame.draw.rect(self.screen, (0, 255, 0), (pos_x, pos_y - 2, (TILE_SIZE-2) * health, 3))

        self.screen.blit(img, (pos_x, pos_y))
    
    def clean():
        pygame.quit()

    def render(self,
               baseSpace: np.ndarray,
               troopSpace: np.ndarray,
               deckSpace: np.ndarray, 
               townhall_level: int,
               destruction_percentage: int,
               stars: int,
               loot_gold: int,
               loot_elixir: int,
               total_gold: int,
               total_elixir: int,
               steps: int,
               total_steps: int,
        ):
        self.screen.fill(DARK_GREEN)
        pygame.draw.rect(self.screen, GRASS_GREEN, (SCENE_PADDING, SCENE_PADDING, SCENE_WIDTH - 2 * SCENE_PADDING, SCENE_HEIGHT - 2 * SCENE_PADDING))

        y_lim, x_lim, _ = baseSpace.shape
        for y in range(y_lim-PADDING):
            for x in range(x_lim-PADDING):
                draw_x = x * TILE_SIZE + SCENE_PADDING
                draw_y = y * TILE_SIZE + SCENE_PADDING
                if self.grid_on:
                    pygame.draw.rect(self.screen, (0, 0, 0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)

        for y in range(y_lim):
            for x in range(x_lim):
                draw_x = x * TILE_SIZE + SCENE_PADDING
                draw_y = y * TILE_SIZE + SCENE_PADDING        
                self.drawBuilding(baseSpace, y, x)


        for troopID in Deck.get_troops_alive_ids(troopSpace):
            self.drawTroops(troopSpace, baseSpace, troopID, townhall_level)

        print(f"""
Destruction: {int(destruction_percentage)},
Starts: {stars}
Gold: ({int(loot_gold)}/{total_gold})
Elixir: ({int(loot_elixir)}/{total_elixir})
Time: ({steps}/{total_steps})
""")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        self.clock.tick(1000/MILISECONDS_PER_FRAME)
        pygame.display.update()
                
