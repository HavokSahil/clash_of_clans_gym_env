import pygame
import pygame_gui

import pickle

from GameObject.warbase import Base
from GameObject.buildings import BaseBuilding, DefenseBuilding

from utils import resource_path

class BaseDesignScreen:

    TILE_SIZE = 16

    def __init__(self, manager,
                 base: Base,
                 back_callback,
                 next_callback,
                 load_callback,
        ):

        self.base = base
        self.townHallLevel = self.base.townHallLevel
        self.manager = manager

        self.back_callback = back_callback
        self.next_callback = next_callback
        self.load_callback = load_callback

        self.ui_elements = []

        self.buttons = {
            "random": None,
            "clear": None,
            "save": None,
            "back": None,
            "load": None,
            "next": None,
        }

        self.currently_placing_building = None
        self.currently_placing_building_object = None

        self.building_place_buttons = {}
        self.building_rem_count_labels = {}

        self.image_cache = {}

        self.hovered_tile = (-1, -1)
        self.mousePressed = False
        self.clearing = False
        self.buildingIDtoBeCleared = -1

        self.isLoading = False
        self.isSaving = False

    def on_enter(self):

        self.panel_menu = pygame_gui.elements.UIPanel(
            relative_rect=pygame.rect.Rect(720, 0, 560, 720),
            manager=self.manager,
        )
        self.scenePanel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(-4, -4, 724, 724),
            manager=self.manager,
            object_id="#scenePanel"
        )

        self.mountBuildingScroll()
        self.mountButtons()
        self.mountScenePanel()

        self.ui_elements = [
            self.panel_menu,
            self.scenePanel,
        ]

    def mountScenePanel(self):
        innerSceneSurface = pygame.surface.Surface((656, 656))
        innerSceneSurface.fill((66, 141, 60))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(31, 31, 656, 656),
            image_surface=innerSceneSurface,
            manager=self.manager,
            container=self.scenePanel
        )


    def mountBuildingScroll(self):

        self.building_scroll_area = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.rect.Rect(60, 70, 452, 396),
            manager=self.manager,
            container=self.panel_menu,
        )

        availableBuildings = self.base.getAllBuildings()

        import math
        card_count = len(availableBuildings)
        n_row =math.ceil(card_count / 3)
        self.building_scroll_area.set_scrollable_area_dimensions((424, 206 * n_row))
        self.building_scroll_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.rect.Rect(0, 0, 424, 206 * n_row),
            manager=self.manager,
            container=self.building_scroll_area,
        )

        for idx, (name, level) in enumerate(availableBuildings):
            row = idx // 3
            col = idx % 3

            y = 206 * row
            x = 152 * col

            building = self.base.getBuildingObject(name)

            path = building.getImagePath()
            if not path in self.image_cache:
                self.image_cache[name] = pygame.image.load(resource_path(path), f"{name} image")
            
            panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.rect.Rect(x, y, 120, 190),
                manager=self.manager,
                container=self.building_scroll_panel,
                object_id="#building_card"
            )

            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(20, 10 , 80, 80),
                image_surface=self.image_cache[name],
                manager=self.manager,
                container=panel
            )

            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, 100, 80, 20),
                text=f"{name[:9]}",
                manager=self.manager,
                container=panel,
                object_id="#building_card_text_head"
            )

            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, 120, 80, 20),
                text=f"Level {level}",
                manager=self.manager,
                container=panel,
                object_id="#building_card_text"
            )
            self.building_rem_count_labels[name] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, 140, 80, 20),
                text=f"x{self.base.getBuildingMaxCount(name) - self.base.getBuildingCount(name)} rem",
                manager=self.manager,
                container=panel,
                object_id="#building_card_text"
            )

            self.building_place_buttons[name] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(-2, 160, 120, 30),
                text="Place",
                manager=self.manager,
                container=panel,
                object_id="#btn_building_card_place"
            )

    def mountButtons(self):
        self.panel_opt_buttons = pygame_gui.elements.UIPanel(
            relative_rect=pygame.rect.Rect(60, 567, 424, 116),
            manager=self.manager,
            container=self.panel_menu,
        )

        for idx, key in enumerate(self.buttons.keys()):
            row = idx // 3
            col = idx % 3
            y = 66 * row
            x = 152 * col

            self.buttons[key] = pygame_gui.elements.UIButton(
                relative_rect=pygame.rect.Rect(x, y, 120, 50),
                text=key.capitalize(),
                manager=self.manager,
                container=self.panel_opt_buttons,
                object_id="#btn_base_design"
            )

    def loadImage(self, path, width, height):
        if not path in self.image_cache:
            image = pygame.image.load(resource_path(path)).convert_alpha()
            image = pygame.transform.scale(image, (width, height))
            self.image_cache[path] = image
        return self.image_cache[path]

    def refresh_rem_count_label(self, name: str = None, refresh_all = False):
        if refresh_all:
            for _name, label in self.building_rem_count_labels.items():
                rem = self.base.getBuildingMaxCount(_name) - self.base.getBuildingCount(_name)
                self.building_rem_count_labels[_name].set_text(
                    f"x{rem} rem"
                )
            return
        rem = self.base.getBuildingMaxCount(name) - self.base.getBuildingCount(name)
        self.building_rem_count_labels[name].set_text(
            f"x{rem} rem"
        )
                
    def looperHoverPlacement(self, surface: pygame.surface.Surface):

        if self.currently_placing_building == None \
        or self.currently_placing_building_object == None \
        or self.hovered_tile == (-1, -1):
            return
        
        y, x = self.hovered_tile

        if not (0 <= y < 45 and 0 <= x < 45): return
        
        height = self.currently_placing_building_object.getHeight()
        width = self.currently_placing_building_object.getWidth()

        if y + height >= 45:
            height = 45 - y
        if x + width >= 45:
            width = 45 - x

        building_background_color = (255, 0, 0)

        if self.base.canPlaceBuilding(self.currently_placing_building_object, y, x):
            building_background_color = (0, 255, 0)

        height *= BaseDesignScreen.TILE_SIZE
        width *= BaseDesignScreen.TILE_SIZE
            
        y *= BaseDesignScreen.TILE_SIZE
        x *= BaseDesignScreen.TILE_SIZE

        pygame.draw.rect(
            surface,
            building_background_color,
            (x, y, width, height),
            200
        )

        true_width = self.currently_placing_building_object.getWidth() * BaseDesignScreen.TILE_SIZE
        true_height = self.currently_placing_building_object.getHeight() * BaseDesignScreen.TILE_SIZE

        if true_width != width or true_height != height:
            return


        if self.currently_placing_building_object.type == BaseBuilding.TYPE_DEFENSE:
            assert(isinstance(self.currently_placing_building_object, DefenseBuilding))
            minRange = self.currently_placing_building_object.getMinRange()
            maxRange = self.currently_placing_building_object.getMaxRange()

            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (x + true_width // 2, y + true_height // 2),
                (minRange * self.TILE_SIZE),
                2
            )

            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (x + true_width // 2, y + true_height // 2),
                (maxRange * self.TILE_SIZE),
                2
            )

        building_image = self.loadImage(
            self.currently_placing_building_object.getImagePath(),
            true_width,
            true_height
        )

        surface.blit(building_image, (x, y))

    def looperPlaceBuilding(self):
        if not self.currently_placing_building or \
        not self.currently_placing_building_object or \
        self.hovered_tile == (-1, -1) \
        or not self.mousePressed: return
            
        y, x = self.hovered_tile
        
        if not self.base.placeBuilding(self.currently_placing_building_object, y, x):
            # Works fine, supressing debug messages
            # print(f"Something unexpected happened! While placing building {self.currently_placing_building} at {(y, x)}")
            pass
        self.refresh_rem_count_label(self.currently_placing_building)
        rem = self.base.getBuildingMaxCount(self.currently_placing_building) - self.base.getBuildingCount(self.currently_placing_building)
        if not rem:
            self.handlePressPlaceKey(self.currently_placing_building)
        else:
            self.currently_placing_building_object = self.base.getBuildingObject(self.currently_placing_building)


    def looperDrawBase(self, surface: pygame.surface.Surface):
        for buildingId, (building, position) in self.base.placedBuildings.items():
            height = building.getHeight() * BaseDesignScreen.TILE_SIZE
            width = building.getWidth() * BaseDesignScreen.TILE_SIZE
            image = self.loadImage(building.getImagePath(), width=width, height=height)
            y, x = position.y * BaseDesignScreen.TILE_SIZE, position.x * BaseDesignScreen.TILE_SIZE
            surface.blit(image, (x, y))

    def looperClear(self, surface: pygame.surface.Surface):
        if not self.clearing: return
        y, x = self.hovered_tile
        if not self.base.isTileValid(y, x): return
        buildingID, building, position = self.base.getBuildingFromPosition(y, x)
        if buildingID == -1: return

        self.buildingIDtoBeCleared = buildingID
        
        anchor_x = position.x * BaseDesignScreen.TILE_SIZE
        anchor_y = position.y * BaseDesignScreen.TILE_SIZE
        width = building.width * BaseDesignScreen.TILE_SIZE
        height = building.height * BaseDesignScreen.TILE_SIZE


        pygame.draw.rect(
            surface,
            (255, 0, 0),
            (anchor_x, anchor_y, width, height),
            200
        )

        if self.mousePressed:
            # Delete the building
            self.base.removeBuilding(buildingID)
            self.refresh_rem_count_label(building.name)

    def handlePressPlaceKey(self, key):
        if self.currently_placing_building == key:  # Meaning Cancel is Clicked
            self.building_place_buttons[key].set_text("Place")
            self.currently_placing_building = None
            self.currently_placing_building_object = None
            return
        
        self.turnOffAllAnnotations()
        remCount = self.base.getBuildingMaxCount(key) - self.base.getBuildingCount(key)
        if not remCount: return
        self.currently_placing_building = key
        self.currently_placing_building_object = self.base.getBuildingObject(key)
        for _key in self.building_place_buttons.keys():
            self.building_place_buttons[_key].set_text("Place")
        self.building_place_buttons[key].set_text("Cancel")

    def handleTileHover(self, pos):
        x = pos[0] // BaseDesignScreen.TILE_SIZE
        y = pos[1] // BaseDesignScreen.TILE_SIZE

        self.hovered_tile = (y, x)

    def handleClickReset(self):
        self.base.clear()
        self.turnOffAllAnnotations()

    def handleClickClear(self):
        flag = not self.clearing
        self.turnOffAllAnnotations()
        self.clearing = flag
        if self.clearing: self.buttons["clear"].set_text("Stop")
        else:
            self.buttons["clear"].set_text("Clear")
            self.buildingIDtoBeCleared = -1

    def handlePressRandom(self):
        self.handleClickReset()
        self.base.fillRandomly()
        self.turnOffAllAnnotations()

    def saveBase(self, filename: str):
        with open(filename, "wb") as f:
            pickle.dump(self.base, f)
        self.isSaving = False

    def show_message(self, message: str, title: str):
        self.message_window = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(840, 100, 340, 400),
            manager=self.manager,
            window_title=title,
            html_message=f"<p>{message}</p>"
        )

    def loadBase(self, filename: str):
        with open(filename, "rb") as f:
            _base = pickle.load(f)
        if self.townHallLevel == _base.townHallLevel:
            self.base = _base
            self.load_callback(self.base)
            self.turnOffAllAnnotations()
            self.isLoading = False
        else:
            self.show_message(f"The file contains base for Different Townhall (Level: {_base.townHallLevel})", title="Invalid Action")

    def turnOffAllAnnotations(self):
        self.currently_placing_building = None
        self.currently_placing_building_object = None
        self.clearing = False
        self.buildingIDtoBeCleared = -1
        for _key in self.building_place_buttons.keys():
            self.building_place_buttons[_key].set_text("Place")
        self.buttons["clear"].set_text("Clear")
        self.refresh_rem_count_label(None, True)


    def openFileSaveDialog(self):
        self.isSaving = True
        self.baseSaveDialog = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect(840, 100, 340, 400),
            manager=self.manager,
            window_title="Save Base Layout",
            initial_file_path="my_base_layout.pkl",
            allow_existing_files_only=False
        )

    def openFileLoadDialog(self):
        self.isLoading = True
        self.baseSaveDialog = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect(840, 100, 340, 400),
            manager=self.manager,
            window_title="Load Base Layout",
            initial_file_path="my_base_layout.pkl",
            allow_existing_files_only=True
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for key, button in self.building_place_buttons.items():
                if event.ui_element == button:
                    self.handlePressPlaceKey(key)

            for key, button in self.buttons.items():
                if event.ui_element == button:
                    if (key == "back"):
                        # Fall back to townhall selection
                        self.back_callback()
                    if (key == "reset"):
                        self.handleClickReset()
                    if (key == "random"):
                        self.handlePressRandom()
                    if (key == "clear"):
                        self.handleClickClear()
                    if (key == "save"):
                        self.openFileSaveDialog()
                    if (key == "load"):
                        self.openFileLoadDialog()
                    if (key == "next"):
                        self.next_callback(self.townHallLevel)
        
        elif event.type == pygame.MOUSEMOTION:
            self.handleTileHover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mousePressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.mousePressed = False

        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if self.isLoading:
                self.loadBase(event.text)
            if self.isSaving:
                self.saveBase(event.text)

    def update(self, dt):
        pass

    def draw_grid(self, surface: pygame.Surface):
        for i in range(45):
            for j in range(45):
                y = i * BaseDesignScreen.TILE_SIZE
                x = j * BaseDesignScreen.TILE_SIZE
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (x, y, BaseDesignScreen.TILE_SIZE, BaseDesignScreen.TILE_SIZE), 1)

    def draw(self, surface: pygame.Surface):

        # if self.currently_placing_building is not None:
        #     self.draw_grid(surface)
        
        self.looperClear(surface)

        self.looperDrawBase(surface)

        if self.currently_placing_building is not None:
            self.looperPlaceBuilding()
            self.looperHoverPlacement(surface)

    def clean_up(self):
        for elem in self.ui_elements:
            elem.kill()
        self.ui_elements = []
