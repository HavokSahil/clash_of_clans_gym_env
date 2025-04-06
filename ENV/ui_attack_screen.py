import threading

import pygame
import pygame_gui
import numpy as np

from GameObject.warbase import Base
from GameObject.deck import Deck
from GameObject.warzone import Warzone
from GameObject.buildings import BuildingDirectory
from GameObject.config import *
from GameObject.troops import *

from training_progress_callback import *

from coc_env import WarzoneEnv

path_star_filled = "images/icons/shiny_star.png"
path_star_empty  = "images/icons/dark_star.png"

class AttackScreen:

    TILE_SIZE = 720 // 45

    def __init__(
            self,
            manager,
            base: Base,
            deck: Deck,
            back_callback,
    ):
        
        self.manager = manager
        self.base  = base
        self.deck = deck

        self.back_callback = back_callback 
        self.townHallLevel = self.base.townHallLevel

        self.warzone_env = WarzoneEnv(
            self.townHallLevel,
            self.base,
            self.deck,
            is_rendering=False
        )

        self.obs, _ = self.warzone_env.reset()

        self.selected_deck_card = None

        self.training_stop_event = None

        self.attack_mode_human = True
        self.training_in_progress = False
        self.image_cache = {}
        self.hovered_tile = (-1, -1)
        self.mouse_pressed = False
        self.is_attack_running = False

        self.model = None

        self.buttons = {
            "mode": None,
            "train": None,
            "weight": None,
            "back": None,
            "reset": None,
            "attack": None
        }

        self.troop_buttons = {}
        self.troop_count_labels = {}

        self.ms_since_last_updated = 0
        self.last_deployment_time = 0

        self.ui_elements = []

    def can_deploy(self):
        return pygame.time.get_ticks() - self.last_deployment_time > 200
    
    def load_model(self):
        from stable_baselines3 import PPO
        self.model = PPO.load("ppo_model", env=self.warzone_env)
        self.obs, info = self.warzone_env.reset()

    def on_enter(self):

        self.scene_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 720, 720),
            manager = self.manager,
            object_id="#panel_atk_scrn_scene"
        )

        self.menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(720, 0, 560, 720),
            manager=self.manager,
        )

        self.attack_mode_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(380, 680, 150, 20),
            manager=self.manager,
            text=f"{"Human" if self.attack_mode_human else "AI"} is attacking",
            container=self.menu_panel,
        )

        self.time_left_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(320, 30, 180, 44),
            text="3:00 left",
            manager=self.manager,
            container=self.menu_panel,
            object_id="#rem_time_label"
        )

        self.mountScenePanel()
        self.mountButtonPanel()
        self.mountStatusBars()
        self.mountDeckPoint()
        self.mountStarsPanel()
        self.mountTrainProgressBar()

        self.ui_elements = [
            self.scene_panel,
            self.menu_panel
        ]

    def getBaseSpace(self):
        return self.warzone_env.warzone.baseSpace
    
    def getTroopSpace(self):
        return self.warzone_env.warzone.troopSpace
    
    def getDeckSpace(self):
        return self.warzone_env.warzone.deckSpace
    
    def getDestructionPercentage(self):
        return int(self.warzone_env.warzone.destruction_percentage)
    
    def getTotalElixir(self):
        return self.warzone_env.warzone.total_elixir
    
    def getLootedElixir(self):
        return int(self.warzone_env.warzone.loot_elixir)
    
    def getTotalGold(self):
        return self.warzone_env.warzone.total_gold
    
    def getLootedGold(self):
        return int(self.warzone_env.warzone.loot_gold)
    
    def getStoredGoldFraction(self) -> float:
        loot = self.getLootedGold()
        total = self.getTotalGold()
        return (total - loot) / total if total else 0.0
    
    def getStoredElixirFraction(self) -> float:
        loot = self.getLootedElixir()
        total = self.getTotalElixir()
        return (total - loot) / total if total else 0.0
      
    def getStars(self) -> int:
        return self.warzone_env.warzone.stars

    def mountScenePanel(self):
        innerSceneSurface = pygame.surface.Surface((656, 656))
        innerSceneSurface.fill((118, 92, 43))
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(31, 31, 656, 656),
            image_surface=innerSceneSurface,
            manager=self.manager,
            container=self.scene_panel
        )

    def mountButtonPanel(self):
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(172, 562, 350, 120),
            manager=self.manager,
            container=self.menu_panel,
        )

        for idx, key in enumerate(self.buttons.keys()):
            row = idx // 3
            col = idx % 3

            y = row * 60
            x = col * 120

            self.buttons[key] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, 110, 50),
                manager=self.manager,
                text=key.capitalize(),
                container=panel,
                object_id="#btn_warzone"
            )

    def mountStarsPanel(self):
        self.starsPanel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(320, 90, 180, 60),
            manager=self.manager,
            container=self.menu_panel,
        )
        stars = self.getStars()

        self.star_images = []

        filled_star = self.loadImage(path_star_filled, 50, 50)
        empty_star = self.loadImage(path_star_empty, 50, 50)

        for i in range(3):

            y = 0
            x = 60 * i

            self.star_images.append(pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(x, y, 50, 50),
                image_surface=filled_star if i < stars else empty_star,
                manager=self.manager,
                container=self.starsPanel
            ))

    def mountStatusBars(self):
        statusBarPanel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(200, 190, 320, 240),
            container=self.menu_panel,
            manager=self.manager
        )

        self.gold_status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 300, 32),
            text=f"Loot Gold: ({self.getLootedGold()} / {self.getTotalGold()})",
            container=statusBarPanel
        )
        self.gold_status_bar = pygame_gui.elements.UIStatusBar(
            relative_rect=pygame.Rect(0, 40, 300, 32),
            container=statusBarPanel,
            percent_method=lambda : self.getStoredGoldFraction(),
            object_id="#gold_status_bar",
        )
        self.elixir_status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 80, 300, 32),
            text=f"Loot Elixir: ({self.getLootedElixir()} / {self.getTotalElixir()})",
            container=statusBarPanel
        )
        self.elixir_status_bar = pygame_gui.elements.UIStatusBar(
            relative_rect=pygame.Rect(0, 120, 300, 32),
            container=statusBarPanel,
            percent_method=lambda : self.getStoredElixirFraction(),
            object_id="#elixir_status_bar"
        )
        self.destruction_percentage_status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 160, 300, 32),
            text=f"Destruction %age: {self.getDestructionPercentage()}%",
            container=statusBarPanel
        )
        self.destruction_percentage_status_bar = pygame_gui.elements.UIStatusBar(
            relative_rect=pygame.Rect(0, 200, 300, 32),
            container=statusBarPanel,
            percent_method=lambda : self.getDestructionPercentage() / 100,
            object_id="#dest_perc_status_bar"
        )

    def mountDeckPoint(self):
        troops = self.deck.getAllowedTroopsForTownhall()
        
        panel_height = 80 * len(troops) + 10 * (len(troops) - 1)
        panel_width = 150

        y = 360 - panel_height // 2
        x = 0

        deckPanel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, panel_width, panel_height),
            manager=self.manager,
            container=self.menu_panel,
        )

        for idx, troop in enumerate(troops):

            troop_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(0, idx * 90, 150, 80),
                manager=self.manager,
                container=deckPanel,
                object_id="#troop_panel"
            )

            image = self.loadImage(
                TroopBase.getImagePathFromName(troop),
                80,
                80
            )

            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(0, 0, 80, 80),
                image_surface=image,
                manager=self.manager,
                container=troop_panel
            )

            self.troop_buttons[troop] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, idx * 90, 150, 80),
                manager=self.manager,
                text="",
                container=deckPanel,
                object_id="#invisible_btn",
                starting_height=10
            )
            self.troop_count_labels[troop] = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(70, idx * 90, 80, 80),
                manager=self.manager,
                text=f"x{self.deck.getTroopCount(troop)}",
                container=deckPanel,
                object_id="@card_bold"
            )

    def mountTrainProgressBar(self):
        self.progress_dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect(840, 100, 340, 400),
            manager = self.manager,
            window_title="Training Progress",
            action_long_desc="PPO Training in Progress",
            action_short_name="Close",
            blocking=True
        )
        self.progress_dialog.hide()
        self.progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((20, 130, 260, 20)),
            manager = self.manager,
            container=self.progress_dialog,
        )
        self.progress_bar.set_current_progress(0)

    def drawBuilding(self, surface: pygame.Surface, y: int, x: int):
        true_y = y * self.TILE_SIZE
        true_x = x * self.TILE_SIZE

        buildingID = Base.get_buildingID_for_position(self.getBaseSpace(), (y, x))
        if buildingID == -1: return

        locations = Base.get_building_location(self.getBaseSpace(), buildingID)

        y_beg = locations[0][0]
        x_beg = locations[1][0]

        if (y, x) != (y_beg, x_beg): return

        level = Base.get_building_property(self.getBaseSpace(), buildingID, "building_level")
        objID = Base.get_building_property(self.getBaseSpace(), buildingID, "building_object_identifier")

        buildingObject = BuildingDirectory.getBuildingObjectFromID(objID, level)

        hp_max = buildingObject.getHp()
        hp_rem = Base.get_building_property(self.getBaseSpace(), buildingID, "building_remaining_hp")

        health = hp_rem / (hp_max * SCALE_FACTOR) if hp_max != 0 else 0.0

        if health == 0:
            # Destroyed Building
            return
    
        if health < 1:
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (true_x + 4, true_y - 2, self.TILE_SIZE * buildingObject.width - 8, 3)
            )
            pygame.draw.rect(
                surface,
                (0, 255, 0),
                (true_x + 4, true_y - 2, (self.TILE_SIZE * buildingObject.width - 8) * health, 3)
            )


        width = buildingObject.height * self.TILE_SIZE
        height = buildingObject.width * self.TILE_SIZE

        img = self.loadImage(buildingObject.getImagePath(), width, height)
        surface.blit(img, (true_x, true_y))

    def drawAllBuildings(self, surface: pygame.Surface):
        ylim, xlim, _ = self.getBaseSpace().shape
        for y in range(ylim):
            for x in range(xlim):
                self.drawBuilding(surface, y, x)

    def drawTroop(self, surface: pygame.Surface, troopID: int):
        if troopID == -1: return

        deckID = Deck.get_troop_deckID(self.getTroopSpace(), troopID)
        troopObject = Deck.getTroopObjectFromDeckID(deckID, self.townHallLevel)

        hp_max = troopObject.getHP()
        hp_rem = Deck.get_troop_hp(self.getTroopSpace(), troopID, unscaled=True)

        # Highlight Target
        targetID = Deck.get_troop_target_building(self.getTroopSpace(), troopID)
        if targetID != -1:
            locations = Base.get_building_location(self.getBaseSpace(), targetID)
            target_y = locations[0][0] * self.TILE_SIZE
            target_x = locations[1][0] * self.TILE_SIZE
            from math import sqrt
            width = int(sqrt(len(locations[0]))) * self.TILE_SIZE
            
            # !!!GPT CODE BEGIN
            area_width = int(sqrt(len(locations[0]))) * self.TILE_SIZE

            rect_scale = 0.5  # adjust as needed (0.5 means half size)
            rect_width = int(area_width * rect_scale)

            offset = (area_width - rect_width) // 2
            rect_x = target_x + offset
            rect_y = target_y + offset

            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (rect_x, rect_y, rect_width, rect_width),
                2
            )

            # !!!GPT CODE END

        health = hp_rem / hp_max

        img = self.loadImage(
            troopObject.getAvatarPath(),
            self.TILE_SIZE,
            self.TILE_SIZE
        )

        troop_y, troop_x = Deck.get_troop_pos(self.getTroopSpace(), troopID, unscaled=True)

        true_y = troop_y * self.TILE_SIZE
        true_x = troop_x * self.TILE_SIZE

        if health < 1:
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (true_x, true_y - 2, self.TILE_SIZE-2, 3)
            )

            pygame.draw.rect(
                surface,
                (0, 255, 0),
                (true_x, true_y - 2, (self.TILE_SIZE-2) * health, 3)
            )
        
        surface.blit(img, (true_x, true_y))

    def drawAllTroops(self, surface: pygame.Surface):
        for troopID in Deck.get_troops_alive_ids(self.getTroopSpace()):
            self.drawTroop(surface, troopID)

    def loadImage(self, path, width, height):
        if (path, width, height) not in self.image_cache:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (width, height))
            self.image_cache[(path, width, height)] = image
        return self.image_cache[(path, width, height)]

    def looperHover(self, surface: pygame.Surface):
        
        if self.selected_deck_card == None: return
        y, x = self.hovered_tile
        if not (0 <= y < 45 and 0 <= x < 45): return
        deckID = Deck.DECK_NAME_MAPS_ID[self.selected_deck_card]
        if Deck.get_deck_member_count(self.warzone_env.warzone.deckSpace, deckID) > 0:
            img = self.loadImage(
                TroopBase.getImagePathFromName(self.selected_deck_card),
                int(self.TILE_SIZE * 1.2),
                int(self.TILE_SIZE * 1.2),
            )
        
            true_y = y * self.TILE_SIZE
            true_x = x * self.TILE_SIZE

            surface.blit(img, (true_x, true_y))

    def update_troop_deployment(self):
        for name, label in self.troop_count_labels.items():
            memberID = Deck.DECK_NAME_MAPS_ID[name]
            label.set_text(f"x{Deck.get_deck_member_count(self.warzone_env.warzone.deckSpace, memberID)}")

    def updateTimeLabel(self):

        steps_passed = self.warzone_env.warzone.timestep
        steps_max = self.warzone_env.warzone.maxtimestep
        ms_per_frame = MILISECONDS_PER_FRAME

        remaining_time_ms = (steps_max - steps_passed) * ms_per_frame
        remaining_time_s = int(remaining_time_ms / 1000)
        remaining_time_m = remaining_time_s // 60
        timer_seconds = remaining_time_s % 60

        time_string = f"{remaining_time_s}s left" if not remaining_time_m else \
            f"{remaining_time_m}:{str(timer_seconds).rjust(2, '0')} left"
        
        self.time_left_label.set_text(time_string)

    def updateLootLabel(self):
        self.gold_status_label.set_text(f"Loot Gold: ({self.getLootedGold()} / {self.getTotalGold()})")
        self.elixir_status_label.set_text(f"Loot Elixir: ({self.getLootedElixir()} / {self.getTotalElixir()})")
        self.destruction_percentage_status_label.set_text(f"Destruction %age: {self.getDestructionPercentage()}%")

    def updateStarsPanel(self):
        stars = self.getStars()

        filled_star = self.loadImage(path_star_filled, 50, 50)
        empty_star = self.loadImage(path_star_empty, 50, 50)

        for i in range(3):
            self.star_images[i].set_image(filled_star if i<stars else empty_star)

    def updateStatusWidgets(self):
        self.updateStarsPanel()
        self.update_troop_deployment()
        self.updateTimeLabel()
        self.updateLootLabel()

    def handleTileHover(self, pos):
        x = pos[0] // self.TILE_SIZE
        y = pos[1] // self.TILE_SIZE

        self.hovered_tile = (y, x)

    def handleClickDeckCard(self, name: str):
        if not self.attack_mode_human or self.selected_deck_card == name:
            self.selected_deck_card = None
            return
        
        self.selected_deck_card = name

    def setMode(self, human=True):
        self.attack_mode_human = human
        self.attack_mode_label.set_text(f"{"Human" if human else "AI"} is attacking")

    def handleClickMode(self):
        if self.attack_mode_human: self.setMode(False)
        else: self.setMode(True)

    def setAttackModes(self, start = True):
        self.is_attack_running = start
        self.buttons["attack"].set_text("Stop" if start else "Start")

    def handleClickAttack(self):
        if self.is_attack_running: self.setAttackModes(False)
        else:
            self.setAttackModes(True)
            if not self.attack_mode_human:
                self.load_model()

    def handleClickReset(self):
        self.setAttackModes(False)
        self.setMode(True)
        self.warzone_env = WarzoneEnv(self.townHallLevel, self.base, self.deck, is_rendering=False)
        self.updateStatusWidgets()
        self.training_in_progress = False
        self.model = None
        self.on_cancel_training()

    def handleClickTrain(self):
        if not self.training_in_progress:
            self.progress_dialog.set_display_title("Training in Progress...")
            self.progress_bar.set_current_progress(0)
            self.progress_dialog.show()
            # TODO call the training function
            self.training_stop_event = threading.Event()
            self.training_thread = train_ppo_model(
                self.warzone_env,
                10000,
                self.update_progress,
                self.training_finished,
                stop_event = self.training_stop_event
            )
            self.training_in_progress = True

    def on_cancel_training(self):
        if self.training_stop_event:
            self.training_stop_event.set()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handleTileHover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_pressed = False
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            for key, button in self.buttons.items():
                if event.ui_element == button:
                    if (key == "back"):
                        self.back_callback(self.townHallLevel)
                    elif (key == "mode"):
                        self.handleClickMode()
                    elif (key == "attack"):
                        self.handleClickAttack()
                    elif (key == "reset"):
                        self.handleClickReset()
                    elif (key == "train"):
                        self.handleClickTrain()
            
            for key, button in self.troop_buttons.items():
                if event.ui_element == button:
                    self.handleClickDeckCard(key)

        elif event.type == pygame.USEREVENT:
            if "progress" in event.__dict__:
                value = int(event.progress * 100)
                self.progress_bar.set_current_progress(value)
            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if event.ui_element == self.progress_dialog:
                    self.on_cancel_training()
                    print("Training Cancelled")
                    self.training_in_progress = False
                    self.handleClickReset()
                else:
                    print("Something Else")
            
        elif event.type == pygame.USEREVENT + 1:
            self.progress_dialog.set_display_title("Training Complete")
            self.progress_bar.set_current_progress(100)
            self.training_in_progress = False

    def update_progress(self, progress):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'progress': progress}))

    def training_finished(self):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))

    def draw(self, surface: pygame.Surface):
        if self.training_in_progress: return
        self.drawAllBuildings(surface)
        self.drawAllTroops(surface)
        self.looperHover(surface)

    def update(self, dt):
        if self.training_in_progress: return
        if self.ms_since_last_updated >= MILISECONDS_PER_FRAME:
            self.updateStatusWidgets()
            self.ms_since_last_updated = 0
            return

        self.ms_since_last_updated += int(dt * 1000)

        action = (0, 0, 7)

        # Handle human input
        if self.mouse_pressed and self.selected_deck_card:
            troop_name = self.selected_deck_card
            deckID = Deck.DECK_NAME_MAPS_ID[troop_name]
            y, x = self.hovered_tile
            if self.can_deploy():
                action = (y, x, deckID)
                self.last_deployment_time = pygame.time.get_ticks()

        # AI Mode
        if not self.attack_mode_human:
            if not self.model:
                self.setAttackModes(False)
            else:
                action, _ = self.model.predict(self.obs)

        if self.is_attack_running:
            if self.attack_mode_human:
                obs, reward, done, truncated, info = self.warzone_env.step(action)
            else:
                obs, reward, done, truncated, info = self.warzone_env.step(action)

            self.obs = obs

            if done or truncated:
                self.setAttackModes(False)

    def clean_up(self):
        for element in self.ui_elements:
            element.kill()
        self.ui_elements = []
 