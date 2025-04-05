import pygame
import pygame_gui
import pygame_gui.elements.ui_panel

import pickle

from GameObject.troops import TroopBase
from GameObject.deck import Deck

background_url = "images/scenes/troop_background.png"

class TroopSelectionScreen:
    def __init__(self,
            deck: Deck,
            manager,
            back_callback,
            next_callback
        ):

        self.deck = deck
        self.townHallLevel = self.deck.townHallLevel

        self.manager = manager
    
        self.back_callback = back_callback
        self.next_callback = next_callback
        self.buttons = {
            "load": None,
            "save": None,
            "back": None,
            "next": None
        }
        self.ui_elements = []
        self.troop_buttons = {}

        self.image_cache = {}

        self.troop_count_labels = {}
        self.troop_add_buttons = {}
        self.troop_remove_buttons = {}

        self.isLoading = False
        self.isSaving = False

    def on_enter(self):
        image = pygame.image.load(background_url).convert_alpha()
        self.background_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, 1280, 720),
            manager=self.manager,
            image_surface=image
        )

        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(484, 104, 320, 50),
            manager=self.manager,
            text="Recruit Troops",
            object_id="#troop_recruit_title",
        )

        self.button_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(880, 490, 190, 96),
            manager=self.manager,
            object_id="#btn_panel_troop_recruit"
        )

        self.camp_space_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(880, 400, 190, 60),
            manager=self.manager,
        )

        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 190, 30),
            manager=self.manager,
            container=self.camp_space_panel,
            text="Camp Space",
            object_id="#troop_space_label"
        )

        self.camp_space_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 30, 190, 30),
            manager=self.manager,
            container=self.camp_space_panel,
            text=f"{self.deck.capacity - self.deck.availableSpace()} / {self.deck.capacity}",
            object_id="#troop_space_label"
        )

        self.troop_cards_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(225, 186, 830, 420),
            manager=self.manager,
        )


        self.mount_buttons()
        self.mount_troop_cards()

        self.ui_elements = [
            self.background_image,
            self.title_label,
            self.button_panel,
            self.camp_space_panel,
            self.troop_cards_panel
        ]

    def mount_buttons(self):
        for idx, key in enumerate(list(self.buttons.keys())):
            row = idx // 2
            col = idx % 2

            y = row * 50
            x = col * 100

            self.buttons[key] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, 90, 40),
                manager=self.manager,
                container=self.button_panel,
                text=key.capitalize(),
                object_id="#btn_troops_recruit_action"
            )


    def mount_troop_cards(self):
        for idx, troop in enumerate(self.deck.getAllTroops()[:-1]):
            row = idx // 4
            col = idx % 4

            y = 226 * row
            x = 210 * col

            card_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(x, y, 200, 184),
                manager=self.manager,
                container=self.troop_cards_panel,
                object_id="#panel_troop_card"
            )

            availableTroops = self.deck.getAllowedTroopsForTownhall()

            if troop in availableTroops:

                troopObject = self.deck.getTroopObject(troop)

                image = self.loadImage(
                    troopObject.getImagePath(),
                    width=100,
                    height=100,
                )

                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(0, 0, 100, 100),
                    image_surface=image,
                    container=card_panel,
                    manager=self.manager
                )

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(0, 100, 100, 30),
                    text=f"{troop[:9]}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_bold"
                )

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(0, 130, 100, 20),
                    text=f"lvl {troopObject.level}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_normal"
                )

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(100, 10, 100, 20),
                    text=f"DPH: {int(troopObject.getDph())}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_normal"
                )

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(100, 30, 100, 25),
                    text=f"HP: {troopObject.getHP()}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_bold"
                )
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(100, 55, 100, 20),
                    text=f"Range: {troopObject.getAtkRange()}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_normal"
                )
                msg = "Any"
                if troopObject.getPreference() == TroopBase.PREFER_DEFENSE:
                    msg = "Defense"
                elif troopObject.getPreference() == TroopBase.PREFER_RESOURCE:
                    msg = "Resource"
                elif troopObject.getPreference() == TroopBase.PREFER_WALL:
                    msg = "Wall"

                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(100, 80, 100, 20),
                    text=f"^ {msg}",
                    container=card_panel,
                    manager=self.manager,
                    object_id="@card_normal"
                )

                bottom_panel = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect(-2, 150, 200, 30),
                    manager=self.manager,
                    container = card_panel,
                    object_id="#troop_recruit_bottom_panel"
                )

                self.troop_count_labels[troop] = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(0, 0, 40, 30),
                    text=f"x{self.deck.getTroopCount(troop)}",
                    manager=self.manager,
                    container=bottom_panel
                )
                self.troop_add_buttons[troop] = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(150, -4, 40, 29),
                    text="+",
                    manager=self.manager,
                    container=bottom_panel,
                    object_id="@btn_troop_recruit"
                )
                self.troop_remove_buttons[troop] = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(110, -4, 40, 29),
                    text="-",
                    manager=self.manager,
                    container=bottom_panel,
                    object_id="@btn_troop_recruit"
                )
            
            else:
                pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(20, 72, 160, 40),
                    text=f"{troop[:9]} is Locked",
                    manager=self.manager,
                    container=card_panel,
                    object_id="#troop_locked_label"
                )


    def loadImage(self, path, width, height):
        if not path in self.image_cache:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (width, height))
            self.image_cache[path] = image
        return self.image_cache[path]

    
    def openFileSaveDialog(self):
        self.isSaving = True
        self.deckSaveDialog = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect(300, 100, 680, 400),
            manager=self.manager,
            window_title="Save Deck",
            initial_file_path="my_deck.pkl",
            allow_existing_files_only=False
        )

    def openFileLoadDoalog(self):
        self.isLoading = True
        self.deckLoadDoalog = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect(300, 100, 680, 400),
            manager=self.manager,
            window_title="Load Deck",
            initial_file_path="my_deck.pkl",
            allow_existing_files_only=True
        )

    def show_message(self, message: str, title: str):
        self.message_window = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(300, 100, 680, 400),
            manager=self.manager,
            window_title=title,
            html_message=f"<p>{message}</p>"
        )

    def saveTroopDeck(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.deck, f)
        self.isSaving = False

    def loadTroopDeck(self, filename):
        with open(filename, "rb") as f:
            _deck = pickle.load(f)
        if self.deck.townHallLevel == _deck.townHallLevel:
            self.deck = _deck
            self.isLoading = False
            self.refresh_text_data()
        else:
            self.show_message(f"The file contains deck for Different Townhall (Level: {_deck.townHallLevel})", title="Invalid Action")


    def handle_add_troop(self, name):
        if self.deck.canRecruitTroop(name):
            if self.deck.recruitTroop(name):
                final_count = self.deck.getTroopCount(name)
                self.update_troop_count_label(name, final_count)
        self.update_camp_space_label()

    def handle_remove_troop(self, name):
        if self.deck.disbandTroop(name):
            final_count = self.deck.getTroopCount(name)
            self.update_troop_count_label(name, final_count)

        self.update_camp_space_label()

    def update_troop_count_label(self, name, count):
        self.troop_count_labels[name].set_text(f"x{count}")

    def update_camp_space_label(self):
        self.camp_space_label.set_text(f"{self.deck.capacity - self.deck.availableSpace()} / {self.deck.capacity}")

    def refresh_text_data(self):
        for name in self.troop_add_buttons.keys():
            final_count = self.deck.getTroopCount(name)
            self.update_troop_count_label(name, final_count)
        self.update_camp_space_label()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for key, button in self.buttons.items():
                if event.ui_element == button:
                    if (key == "back"):
                        self.back_callback(self.townHallLevel)
                    if (key == "save"):
                        self.openFileSaveDialog()
                    if (key == "load"):
                        self.openFileLoadDoalog()
            for name, button in self.troop_add_buttons.items():
                if event.ui_element == button:
                    self.handle_add_troop(name)

            for name, button in self.troop_remove_buttons.items():
                if event.ui_element == button:
                    self.handle_remove_troop(name)

        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if self.isLoading:
                self.loadTroopDeck(event.text)
            if self.isSaving:
                self.saveTroopDeck(event.text)

    def update(self, dt):
        pass

    def draw(self, surface: pygame.Surface):
        pass

    def clean_up(self):
        for elem in self.ui_elements:
            elem.kill()
        self.ui_elements = []