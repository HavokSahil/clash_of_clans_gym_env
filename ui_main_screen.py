import pygame
import pygame_gui

from utils import resource_path

background_url = resource_path("images/scenes/floating_island.png")

class MainScreen:
    def __init__(self, manager, onLevelSelected):
        self.manager = manager
        self.onLevelSelected = onLevelSelected
        self.ui_elements = []
        self.buttons = {}

    def on_enter(self):
        self.background_image = pygame.image.load(background_url).convert_alpha()
        self.background_image_rect = self.background_image.get_rect()
        self.background_image_rect.topleft = (0, 0)

        self.background_image = pygame_gui.elements.UIImage(
            relative_rect=self.background_image_rect,
            manager=self.manager,
            image_surface=self.background_image,
        )

        self.label_rect = pygame.Rect(457, 451, 365, 74)
        self.label = pygame_gui.elements.UILabel(
            relative_rect=self.label_rect,
            manager=self.manager,
            text="Select Town Hall Level",
            object_id="#main_screen_label"
        )

        self.panel_rect = pygame.Rect(175, 525, 930, 80)
        self.button_panel = pygame_gui.elements.UIPanel(
            relative_rect = self.panel_rect,
            starting_height=1,
            manager=self.manager,
            object_id="#levels_panel"
        )

        for i in range(1, 6):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(190*(i-1), 0, 170, 80),
                text=f"Level {i}",
                manager=self.manager,
                tool_tip_text=f"Townhall Level {i}",
                container=self.button_panel,
                object_id=pygame_gui.core.ObjectID(class_id=f"@btn_level_cls", object_id=f"#btn_level{i}") 
            )
            self.buttons[f"btn_level{i}"] = button

        self.ui_elements = [
            self.label,
            self.button_panel,
            self.background_image
        ]

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for key, button in self.buttons.items():
                if event.ui_element == button:
                    if str(key).startswith("btn_level"):
                        level = int(str(key)[-1])
                        self.onLevelSelected(level)
            

    def update(self, dt):
        pass

    def draw(self, surface: pygame.Surface):
        pass

    def clean_up(self):
        for elem in self.ui_elements:
            elem.kill()
        self.ui_elements = []