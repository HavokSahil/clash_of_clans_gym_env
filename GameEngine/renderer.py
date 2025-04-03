import time
import math
import copy
import pygame
import pygame_gui
from .base import SceneBase
from .structures import *
from .troops import *
from typing import Tuple, Set

TILE_SIZE = 20  # Each tile is 32x32 pixels
PADDING_SIZE = SceneBase.BASE_PADDING * TILE_SIZE  # Padding space in pixels
SCENE_WIDTH = SceneBase.BASE_WIDTH * TILE_SIZE + 2 * PADDING_SIZE
SCENE_HEIGHT = SceneBase.BASE_HEIGHT * TILE_SIZE + 2 * PADDING_SIZE
SIDEBAR_WIDTH = 300  # Sidebar width for UI
TROOP_PANEL_WIDTH = 320  # panel for troops

WINDOW_WIDTH = SCENE_WIDTH + SIDEBAR_WIDTH + TROOP_PANEL_WIDTH 
WINDOW_HEIGHT = SCENE_HEIGHT

GRASS_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
SIDEBAR_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

class SceneRenderer:
    def __init__(self, scene: SceneBase):
        pygame.init()
        pygame.display.set_caption("Clash of Gargs")
        
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

        self.is_deploying = False
        self.deployable_troopID = set()
        
        # Initialize pygame_gui
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Create a panel for troop cards (separate from buildings)
        self.troop_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SCENE_WIDTH + SIDEBAR_WIDTH, 0), (TROOP_PANEL_WIDTH, WINDOW_HEIGHT)),
            manager=self.manager,
            
        )

        self.troop_scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 0), (TROOP_PANEL_WIDTH, int(WINDOW_HEIGHT * 0.40))),
            manager=self.manager,
            container=self.troop_panel
        )

        self.camp_capacity_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, int(WINDOW_HEIGHT * 0.45)), (300, 30)),
            text=f"Camp Capacity: {self.scene.current_housed_space}/{self.scene.max_housing_space}",
            manager=self.manager,
            container=self.troop_panel
        )

        self.recruited_troop_scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, int(WINDOW_HEIGHT * 0.50)), (TROOP_PANEL_WIDTH, int(WINDOW_HEIGHT * 0.50))),
            manager=self.manager,
            container=self.troop_panel
        )

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

        self.troop_cards = []
        self.populate_troop_sidebar()

        self.recruit_cards = []
        self.populate_recruited_troop_sidebar()


        # Adjust scrollable area based on content
        self.scroll_container.set_scrollable_area_dimensions((SIDEBAR_WIDTH, max(600, len(self.building_cards) * 60)))

    def populate_recruited_troop_sidebar(self):

        for card in self.recruit_cards:
            card.panel.kill()  # Remove the entire panel
        
        self.recruit_cards.clear() 

        y_offset = 10
        group_map = dict()
        for troopID, troop in self.scene.housed_troops.items():
            group_tag = troop.name + str(troop.level)
            if group_tag in group_map:
                group_map[group_tag].add(troopID)
            else:
                group_map[group_tag] = {troopID}

        for group_tag, troopIDs in group_map.items():
            troop = self.scene.housed_troops[list(troopIDs)[0]]
            card = ArmyCard(
                troop_name=troop.name,
                troop_level=troop.level,
                troopIDs=troopIDs, 
                position=(10, y_offset),
                manager=self.manager,
                container=self.recruited_troop_scroll_container,
                deploy_callback=self.deploy_troop,
                disband_callback=self.disband_troop)
            self.recruit_cards.append(card)
            y_offset += 60

        self.recruited_troop_scroll_container.set_scrollable_area_dimensions(
            (TROOP_PANEL_WIDTH, max(int(WINDOW_HEIGHT * 0.5), len(self.recruit_cards) * 60))
        )

    def populate_troop_sidebar(self):
        """Generate troop cards in the troop panel."""
        y_offset = 10  # Start placing from the top

        for troop in self.scene.troops.all_troops():
            troop_card = TroopCard(
                troop=troop,
                max_level=self.scene.troops_max_level[troop.name],
                position=(10, y_offset),
                manager=self.manager,
                container=self.troop_scroll_container,
                recruit_callback=self.recruit_troop,
            )
            self.troop_cards.append(troop_card)
            y_offset += 60  # Space out cards

        # Adjust the scrollable area based on the number of troop cards
        self.troop_scroll_container.set_scrollable_area_dimensions((TROOP_PANEL_WIDTH, max(int(WINDOW_HEIGHT * 0.4), len(self.troop_cards) * 60)))

    def recruit_troop(self, troop: TroopBase):
        if self.scene.current_housed_space == self.scene.max_housing_space:
            self.show_message("Camp is full.")
            return
        self.scene.recruit_troop(copy.deepcopy(troop))
        self.camp_capacity_label.set_text(f"Camp Capacity: {self.scene.current_housed_space}/{self.scene.max_housing_space}")
        self.populate_recruited_troop_sidebar()

    def deploy_troop(self, troopIDs: Set[int]):
        if self.is_deploying and self.deployable_troopID == troopIDs:
            self.is_deploying = False
            self.deployable_troopID.clear()
            return
        
        self.is_deploying = True
        self.deployable_troopID = troopIDs
        self.camp_capacity_label.set_text(f"Camp Capacity: {self.scene.current_housed_space}/{self.scene.max_housing_space}")
        self.populate_recruited_troop_sidebar()

    def disband_troop(self, troopID: int):
        self.scene.disband_troop(troopID)
        self.camp_capacity_label.set_text(f"Camp Capacity: {self.scene.current_housed_space}/{self.scene.max_housing_space}")
        self.populate_recruited_troop_sidebar()


    def populate_sidebar(self):
        """Generate building cards in the sidebar."""
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


        # Draw hovered troop
        if self.is_deploying:
            if len(self.deployable_troopID) != 0:
                _troopID = list(self.deployable_troopID)[0]
                if self.hover_pos[0] != -1 and self.hover_pos[1] != -1:
                    draw_x = self.hover_pos[1] * TILE_SIZE + PADDING_SIZE
                    draw_y = self.hover_pos[0] * TILE_SIZE + PADDING_SIZE
                    troop = self.scene.housed_troops[_troopID]
                    assert(isinstance(troop, TroopBase))
                    img = self.load_image(troop.image_path)
                    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                    self.screen.blit(img, (draw_x, draw_y))


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

        # Draw the Damage percentage
        font = pygame.font.Font(None, 36)
        text = font.render(f"Damage: {round(self.scene.get_damage_percentage(), 2)}%", True, TEXT_COLOR)
        self.screen.blit(text, (10, 10))

        # Draw stars
        path_star_vacant = PATH_PNG_STAR_VACANT
        path_star_filled = PATH_PNG_STAR_FILLED

        star_vacant = pygame.image.load(path_star_vacant).convert_alpha()
        star_filled = pygame.image.load(path_star_filled).convert_alpha()

        star_vacant = pygame.transform.scale(star_vacant, (30, 30))
        star_filled = pygame.transform.scale(star_filled, (30, 30))

        for i in range(3):
            x = SCENE_WIDTH//2 + i * 40 - 60
            y = 5
            if i < self.scene.get_stars():
                self.screen.blit(star_filled, (x, y))
            else:
                self.screen.blit(star_vacant, (x, y))

        # Draw the time
        font = pygame.font.Font(None, 32)
        text = font.render(f"Time Rem: {self.scene.get_rem_time()}", True, TEXT_COLOR)
        self.screen.blit(text, (SCENE_WIDTH//2 + 200, 10))

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
                if self.scene.should_sim_stop():
                    self.handle_press_start()
                    self.show_message("Game has ended.")
                
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
        self.scene.start_time = time.time()
        self.start_button.set_text("Pause Attack" if self.sim_on else "Start Attack")

    def handle_press_clear(self):
        self.scene.clear()

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

    def handle_troop_deploy(self):
        if len(self.deployable_troopID) == 0:
            self.is_deploying = False
        else:  
            _troopID = self.deployable_troopID.pop()
            self.scene.place_troop(_troopID, self.hover_pos[0], self.hover_pos[1])
        
        self.populate_recruited_troop_sidebar()

    def handle_mouse_pressed(self):
        if not self.mouse_pressed: return
        if self.selected_card != -1:
            self.place_building(self.selected_card)
        if self.erase:
            self.handle_click_hovered_building()
        if self.is_deploying:
            self.handle_troop_deploy()


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
                level = int(selected_level.split(" ")[1])
                self.scene.update_level(selected_buildingID, level)

            # On Press escape key
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_deploying = False
                self.deployable_troopID.clear()
                self.erase = False
                self.change_levels = False
                self.selected_card = -1
                self.grid_on = False
                    
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

                    for idx, card in enumerate(self.troop_cards):
                        card.handle_event(event)

                    for idx, card in enumerate(self.recruit_cards):
                        card.handle_event(event)

            self.manager.process_events(event)


class TroopCard:
    def __init__(self, troop: TroopBase, max_level: int, position, manager, container, recruit_callback):
        self.troop = troop
        self.max_level = max_level
        self.manager = manager
        self.container = container
        self.recruit_callback = recruit_callback

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(position, (280, 50)),
            manager=manager,
            container=container
        )

        # Troop name label
        self.label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (100, 30)),
            text=f"{troop.name} (Lv {troop.level})",
            manager=manager,
            container=self.panel
        )

        # Decrease level button
        self.decrease_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120, 10), (30, 30)),
            text="-",
            manager=manager,
            container=self.panel
        )

        # Increase level button
        self.increase_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((160, 10), (30, 30)),
            text="+",
            manager=manager,
            container=self.panel
        )

        # Recruit troop button
        self.recruit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((200, 10), (50, 30)),
            text="Train",
            manager=manager,
            container=self.panel
        )

    def level_change_callback(self, level):
        if 1 <= level <= self.max_level:
            self.troop.set_level(level)
            self.label.set_text(f"{self.troop.name} (Lv {level})")

    def handle_event(self, event):
        """ Handle button clicks. """
        if event.ui_element == self.increase_button:
            self.label.set_text(f"{self.troop.name} (Lv {self.troop.level})")
            self.level_change_callback(self.troop.level + 1)
        elif event.ui_element == self.decrease_button and self.troop.level > 1:
            self.label.set_text(f"{self.troop.name} (Lv {self.troop.level})")
            self.level_change_callback(self.troop.level - 1)
        elif event.ui_element == self.recruit_button:
                self.recruit_callback(self.troop)

class ArmyCard:
    def __init__(self, troop_name: str, troop_level: int, troopIDs: Set[int], position, manager, container, disband_callback, deploy_callback):
        self.troop_name = troop_name
        self.troop_level = troop_level
        self.troopIDs = troopIDs
        self.manager = manager
        self.container = container
        self.deploy_callback = deploy_callback
        self.disband_callback = disband_callback

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(position, (290, 50)),
            manager=manager,
            container=container
        )

        # Troop name label
        self.label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (170, 30)),
            text=f"{troop_name} (Lv {troop_level}) x{len(troopIDs)}",
            manager=manager,
            container=self.panel
        )

        # Place troop button
        self.place_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((180, 10), (60, 30)),
            text="Deploy",
            manager=manager,
            container=self.panel
        )

        # Remove troop button
        self.remove_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((250, 10), (30, 30)),
            text="X",
            manager=manager,
            container=self.panel
        )

    def handle_event(self, event):
        """ Handle button clicks. """
        if event.ui_element == self.place_button:
            self.deploy_callback(self.troopIDs)
        elif event.ui_element == self.remove_button:
            self.disband_callback(self.troopIDs.pop())