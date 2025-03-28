import math
import copy
import pygame
import pygame_gui
from .base import SceneBase
from .structures import *
from .troops import *

TILE_SIZE = 20  # Each tile is 32x32 pixels
PADDING_SIZE = SceneBase.BASE_PADDING * TILE_SIZE  # Padding space in pixels
SCENE_WIDTH = SceneBase.BASE_WIDTH * TILE_SIZE + 2 * PADDING_SIZE
SCENE_HEIGHT = SceneBase.BASE_HEIGHT * TILE_SIZE + 2 * PADDING_SIZE
SIDEBAR_WIDTH = 300  # Sidebar width for UI

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

        self.sim_on = False
        self.selected_card = -1
        self.grid_on = False

        self.mouse_pressed = False

        self.hover_pos = (-1, -1)
        self.hovered_building = None
        self.hovered_building_backup = None
        self.erase = False
        self.change_levels = False
        
        # Initialize pygame_gui
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.manager.set_visual_debug_mode(True)
        
        # Create scrolling container for sidebar
        self.sidebar_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SCENE_WIDTH, 0), (SIDEBAR_WIDTH, WINDOW_HEIGHT)),
            manager=self.manager
        )

        # Set an initially large scrollable area
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 0), (SIDEBAR_WIDTH, int(WINDOW_HEIGHT * 0.70))),
            manager=self.manager,
            container=self.sidebar_panel
        )

        # Start button
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, int(WINDOW_HEIGHT * 0.7) + 10), (SIDEBAR_WIDTH - 20, 50)),
            text="Start Attack",
            manager=self.manager,
            container=self.sidebar_panel
        )

        self.erase_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, int(WINDOW_HEIGHT * 0.7) + 70), (SIDEBAR_WIDTH - 20, 50)),
            text="Erase",
            manager=self.manager,
            container=self.sidebar_panel
        )

        self.clear_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, int(WINDOW_HEIGHT * 0.7) + 130), (SIDEBAR_WIDTH - 20, 50)),
            text="Clear",
            manager=self.manager,
            container=self.sidebar_panel
        )

        self.levels_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, int(WINDOW_HEIGHT * 0.7) + 190), (SIDEBAR_WIDTH - 20, 50)),
            text="Change Level",
            manager=self.manager,
            container=self.sidebar_panel
        )

        self.building_cards = []
        self.card_context = {}
        self.populate_sidebar()

        # Adjust scrollable area based on content
        self.scroll_container.set_scrollable_area_dimensions((SIDEBAR_WIDTH, max(600, len(self.building_cards) * 60)))

    def populate_sidebar(self):
        y_offset = 10
        for building in self.scene.buildings.get_all():
            assert(isinstance(building, BaseStructure))
            _maxCount = self.scene.buildings_max_count[building.name]
            _placedCount = self.scene.placed_buildings_count[building.name] if building.name in self.scene.placed_buildings_count else 0
            _remCount = _maxCount - _placedCount
            card = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((10, y_offset), (SIDEBAR_WIDTH - 20, 50)),
                text=f"{building.name} (Lv {building.level}) - {_remCount} left",
                manager=self.manager,
                container=self.scroll_container
            )
            self.building_cards.append(card)
            self.card_context[len(self.building_cards) - 1] = building
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
                if buildingID == -1:
                    # Create a border around empty tile
                    if self.grid_on:
                        pygame.draw.rect(self.screen, (0, 0, 0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 1)

                buildingPositions = self.scene.building_positions.get(buildingID)    
                if buildingID != -1 and (y, x) == buildingPositions[0]:
                    building = self.scene.placed_buildings[buildingID]
                    assert(isinstance(building, BaseStructure))

                    if self.grid_on:
                        pygame.draw.rect(self.screen, (0, 255, 0), (draw_x, draw_y, TILE_SIZE * building.height, TILE_SIZE * building.width), 2)

                    if self.hovered_building == building:
                        color = (255, 0, 0) if self.erase else (0, 255, 0)
                        pygame.draw.rect(self.screen, color, (draw_x, draw_y, TILE_SIZE * building.height, TILE_SIZE * building.width), 100)
                        if (building.type == BaseStructure.CLASS_DEFENSE):
                            _range_max = building.max_attack_range
                            _range_min = building.min_attack_range

                            pygame.draw.circle(self.screen, (255, 255, 255), (draw_x + TILE_SIZE // 2, draw_y + TILE_SIZE // 2), int(_range_max * TILE_SIZE/100), 2)
                            pygame.draw.circle(self.screen, (255, 255, 255), (draw_x + TILE_SIZE // 2, draw_y + TILE_SIZE // 2), int(_range_min * TILE_SIZE/100), 2)

                    health = building.get_health()
                    # Show the health bar
                    pygame.draw.rect(self.screen, (255, 0, 0), (draw_x + 4, draw_y - 2, TILE_SIZE * building.width - 8, 3))
                    pygame.draw.rect(self.screen, (0, 255, 0), (draw_x + 4, draw_y - 2, (TILE_SIZE * building.width - 8) * health, 3))

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


        if self.grid_on and self.selected_card != -1:
            if self.hover_pos[0] != -1 and self.hover_pos[1] != -1:
                x = self.hover_pos[1] * TILE_SIZE + PADDING_SIZE
                y = self.hover_pos[0] * TILE_SIZE + PADDING_SIZE

                buildingName = self.card_context[self.selected_card].name
                
                building = self.scene.buildings.get(buildingName)
                valid_position = self.scene.can_place_building(self.hover_pos[0], self.hover_pos[1], building.width, building.height)
                # Make the background filled red if not valid
                color = (255, 0, 0) if not valid_position else (0, 255, 0)
                pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE * building.width, TILE_SIZE * building.height), 200)

                if building.type == BaseStructure.CLASS_DEFENSE:
                    assert(isinstance(building, DefenseStructure))
                    _range_max = building.max_attack_range
                    _range_min = building.min_attack_range

                    pygame.draw.circle(self.screen, (255, 255, 255), (x + TILE_SIZE // 2, y + TILE_SIZE // 2), int(_range_max * TILE_SIZE/100), 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), (x + TILE_SIZE // 2, y + TILE_SIZE // 2), int(_range_min * TILE_SIZE/100), 2)

                img = self.load_image(building.get_image_path(), building.width, building.height)
                self.screen.blit(img, (x, y))

    def handle_select_card(self, card_index: int):
        if self.selected_card == card_index:
            self.selected_card = -1
            self.grid_on = False
        else:
            building = self.card_context[card_index]
            _maxCount = self.scene.buildings_max_count[building.name]
            _placedCount = self.scene.placed_buildings_count[building.name] if building.name in self.scene.placed_buildings_count else 0
            _remCount = _maxCount - _placedCount
            if _remCount == 0:
                self.show_message(f"Maximum number of {building.name} buildings placed.")
                return
            self.selected_card = card_index
            self.grid_on = True


    def place_building(self, card_index: int):
        building = self.card_context[card_index]
        # Clear the sidebar selection
        if self.scene.can_place_building(self.hover_pos[0], self.hover_pos[1], building.width, building.height):
            self.scene.place_building(copy.copy(building), self.hover_pos[0], self.hover_pos[1])
            self.building_cards.clear()
            self.card_context.clear()
            self.populate_sidebar()
            self.hover_pos = (-1, -1)

            if self.scene.buildings_max_count[building.name] == self.scene.placed_buildings_count[building.name]:
                self.selected_card = -1
                self.grid_on = False

    def show_message(self, message):
        self.dialog = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect((self.screen.get_width() // 2 - 180, self.screen.get_height() // 2 - 120), (360, 240)),
            manager=self.manager,
            window_title="Info",
            html_message=message
        )

    def show_level_selection(self, name: str, id: int):
        """Display a popup dialog to select a building level."""

        if hasattr(self, 'level_selection_window'):
            self.level_selection_window.kill()  # Remove the UI window
            del self.level_selection_window

        self.level_selection_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((self.screen.get_width() // 2 - 150, self.screen.get_height() // 2 - 100), (300, 200)),
            manager=self.manager,
            window_display_title=f"Select Level for {name}",
        )

        self.selection_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((10, 10), (280, 140)),
            item_list=[f"{id}:Level {i}" for i in range(1, self.scene.buildings_max_level[name] + 1)],
            manager=self.manager,
            container=self.level_selection_window
        )


    def run(self):
        while self.running:
            time_delta = self.clock.tick(self.fps) / 1000.0
            
            if self.sim_on:
                self.scene.transition()
                
            self.current_frame = (self.current_frame + 1) % self.fps

            self.handle_mouse_pressed()
            self.handle_events()
            self.draw_scene()
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()

        pygame.quit()

    def handle_press_start(self):
        if "Town Hall" not in self.scene.placed_buildings_count:
            self.show_message("Town Hall is not placed.")
            return
        self.sim_on = not self.sim_on
        self.start_button.set_text("Pause Attack" if self.sim_on else "Start Attack")

    def handle_press_clear(self):
        for buildingID in list(self.scene.placed_buildings.keys()):
            self.scene.remove_building(buildingID)

        self.building_cards.clear()
        self.card_context.clear()
        self.populate_sidebar()
        self.hovered_building = None

    def handle_press_erase(self):
        self.erase = not self.erase
        self.erase_button.set_text("Erase" if not self.erase else "Leave Erase")

    def handle_press_levels(self):
        self.change_levels = not self.change_levels
        self.levels_button.set_text("Change Level" if not self.change_levels else "Leave Change Level")

    def update_hover_tile(self, pos: Tuple[int, int]):
        if pos[0] in range(PADDING_SIZE, SCENE_WIDTH + PADDING_SIZE) and pos[1] in range(PADDING_SIZE, SCENE_HEIGHT + PADDING_SIZE):
            x = (pos[0] - PADDING_SIZE) // TILE_SIZE
            y = (pos[1] - PADDING_SIZE) // TILE_SIZE
            self.hover_pos = (y, x)

        if self.hover_pos[0] in range(SceneBase.BASE_HEIGHT) and self.hover_pos[1] in range(SceneBase.BASE_WIDTH):
            tile = self.scene.map[self.hover_pos[0], self.hover_pos[1]]
            if tile is not None:
                buildingID = tile["building"]
                if buildingID != -1:
                    self.hovered_building = self.scene.placed_buildings[buildingID]
                else:
                    self.hovered_building = None

    def handle_mouse_pressed(self):
        if not self.mouse_pressed: return
        if self.selected_card != -1:
            self.place_building(self.selected_card)
        if self.erase:
            self.handle_click_hovered_building()


    def handle_click_hovered_building(self):
        if self.hovered_building is not None:
            if self.erase:
                assert(isinstance(self.hovered_building, BaseStructure))
                y, x = self.hovered_building.position
                buildingID = self.scene.map[y, x]["building"]
                self.scene.remove_building(buildingID)
                self.building_cards.clear()
                self.card_context.clear()
                self.populate_sidebar()
                self.hovered_building = None
            else:
                pos = self.hovered_building.position
                buildingID = self.scene.map[pos[0], pos[1]]["building"]
                if self.change_levels:
                    self.show_level_selection(self.hovered_building.name, buildingID)
            
    def handle_events(self):
        """ Handle user interactions like closing the window and UI events. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.update_hover_tile(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_pressed = True
                self.handle_click_hovered_building()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False

            elif event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                selected_level = event.text  # Example: "Level 3"
                selected_buildingID = int(selected_level.split(":")[0])
                building = self.scene.placed_buildings[selected_buildingID]
                building.set_level(int(selected_level.split(" ")[1]))
                    
            elif event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    self.handle_press_start()
                elif event.ui_element == self.erase_button:
                    self.handle_press_erase()
                elif event.ui_element == self.clear_button:
                    self.handle_press_clear()
                elif event.ui_element == self.levels_button:
                    self.handle_press_levels()
                else:
                    for idx, card in enumerate(self.building_cards):
                        if event.ui_element == card:
                            self.handle_select_card(idx)
            self.manager.process_events(event)
