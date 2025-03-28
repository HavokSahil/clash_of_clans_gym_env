import math
import pygame
import pygame_gui
from .base import SceneBase
from .structures import *
from .troops import *

TILE_SIZE = 20  # Each tile is 32x32 pixels
PADDING_SIZE = SceneBase.BASE_PADDING * TILE_SIZE  # Padding space in pixels
SCENE_WIDTH = SceneBase.BASE_WIDTH * TILE_SIZE + 2 * PADDING_SIZE
SCENE_HEIGHT = SceneBase.BASE_HEIGHT * TILE_SIZE + 2 * PADDING_SIZE
SIDEBAR_WIDTH = 200  # Sidebar width for UI

WINDOW_WIDTH = SCENE_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = SCENE_HEIGHT

GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
SIDEBAR_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

class SceneRenderer:
    def __init__(self, scene: SceneBase):
        pygame.init()
        pygame.display.set_caption("Scene Visualizer")
        
        self.scene = scene
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.image_cache = {}

        self.transition_speed = 1
        self.current_frame = 0
        self.fps = 30
        
        # Initialize pygame_gui
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Create scrolling container for sidebar
        self.sidebar_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SCENE_WIDTH, 0), (SIDEBAR_WIDTH, WINDOW_HEIGHT)),
            manager=self.manager
        )

        # Set an initially large scrollable area
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 0), (SIDEBAR_WIDTH, WINDOW_HEIGHT)),
            manager=self.manager,
            container=self.sidebar_panel
        )

        self.building_cards = []
        self.populate_sidebar()

        # Adjust scrollable area based on content
        self.scroll_container.set_scrollable_area_dimensions((SIDEBAR_WIDTH, max(600, len(self.building_cards) * 60)))

    def populate_sidebar(self):
        y_offset = 10
        # for building in self.scene.buildings.values():
        for  i in range(17):
            card = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((10, y_offset), (SIDEBAR_WIDTH - 20, 50)),
                text=f"building.name (Lv building.level)",
                manager=self.manager,
                container=self.scroll_container
            )
            self.building_cards.append(card)
            y_offset += 60

    def load_image(self, image_path, width=1, height=1):
        """ Load and scale images, caching them to optimize performance. """
        if (image_path, width, height) not in self.image_cache:
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.scale(image, (width * TILE_SIZE, height * TILE_SIZE))
            self.image_cache[(image_path, width, height)] = image
        return self.image_cache[(image_path, width, height)]

    def draw_scene(self):
        """ Draw the entire scene. """
        self.screen.fill(DARK_GREEN)  # Background padding color
        pygame.draw.rect(self.screen, GRASS_GREEN, (PADDING_SIZE, PADDING_SIZE,
                                                     SceneBase.BASE_WIDTH * TILE_SIZE,
                                                     SceneBase.BASE_HEIGHT * TILE_SIZE))

        for y in range(SceneBase.BASE_HEIGHT):
            for x in range(SceneBase.BASE_WIDTH):

                draw_x = x * TILE_SIZE + PADDING_SIZE
                draw_y = y * TILE_SIZE + PADDING_SIZE

                tile = self.scene.map[y, x]
                if tile is None:
                    continue

                # Draw buildings (only at their top-left tile)
                buildingID = tile["building"]
                buildingPositions = self.scene.building_positions.get(buildingID)    
                if buildingID != -1 and (y, x) == buildingPositions[0]:
                    building = self.scene.placed_buildings[buildingID]
                    health = building.get_health()
                    # Show the health bar
                    pygame.draw.rect(self.screen, (255, 0, 0), (draw_x, draw_y - 2, TILE_SIZE-2, 3))
                    pygame.draw.rect(self.screen, (0, 255, 0), (draw_x, draw_y - 2, (TILE_SIZE-2) * health, 3))

                    img = self.load_image(building.get_image_path(), building.width, building.height)
                    self.screen.blit(img, (draw_x, draw_y))

                troopIDs = list(tile["troops"])
                tile_center_x = draw_x + TILE_SIZE // 2
                tile_center_y = draw_y + TILE_SIZE // 2
                img_size = int(TILE_SIZE * 1)

                for troopID in troopIDs:
                    troop = self.scene.placed_troops[troopID]
                    assert(isinstance(troop, TroopBase))
                    img = self.load_image(troop.image_path)
                    img = pygame.transform.scale(img, (img_size, img_size))
                    troop_x = tile_center_x - img_size // 2
                    troop_y = tile_center_y - img_size // 2
                    
                    next_tile_y, next_tile_x = troop.get_next_tile()

                    next_tile_x = next_tile_x * TILE_SIZE + PADDING_SIZE
                    next_tile_y = next_tile_y * TILE_SIZE + PADDING_SIZE 

                    # Interpolate between current tile and next tile
                    troop_x += int((next_tile_x - troop_x) * ((troop.move_timer+1)/troop.max_move_timer))
                    troop_y += int((next_tile_y - troop_y) * ((troop.move_timer+1)/troop.max_move_timer))

                    troop_health = troop.current_hitpoint / troop.get_max_hit_point()

                    pygame.draw.rect(self.screen, (255, 0, 0), (troop_x, troop_y - 2, TILE_SIZE-2, 3))
                    pygame.draw.rect(self.screen, (0, 255, 0), (troop_x, troop_y - 2, (TILE_SIZE-2) * troop_health, 3))

                    self.screen.blit(img, (troop_x, troop_y))

    def run(self):
        while self.running:
            time_delta = self.clock.tick(self.fps) / 1000.0
            
            self.scene.transition()
                
            self.current_frame = (self.current_frame + 1) % self.fps

            self.handle_events()
            self.draw_scene()
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

        pygame.quit()

    def handle_events(self):
        """ Handle user interactions like closing the window and UI events. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.manager.process_events(event)
