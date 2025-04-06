import pygame
import pygame_gui

from GameObject.warbase import Base
from GameObject.deck import Deck

from ui_state_manager import StateManager
from ui_main_screen import MainScreen
from ui_base_design_screen import BaseDesignScreen
from ui_troop_screen import TroopSelectionScreen
from ui_attack_screen import AttackScreen

class App:

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    def __init__(self):
        
        pygame.init()
        pygame.display.set_caption("Clash of Clans AI")

        self.deck = None
        self.base = None

        self.townHallLevel = -1

        self.window = pygame.display.set_mode((App.SCREEN_WIDTH, App.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.manager = pygame_gui.UIManager((App.SCREEN_WIDTH, App.SCREEN_HEIGHT))
        self.manager.add_font_paths(
            font_name="pixelify",
            regular_path="fonts/PixelifySans-Regular.ttf",
            bold_path="fonts/PixelifySans-Bold.ttf",
        )
        self.manager.add_font_paths(
            font_name="fira code",
            regular_path="fonts/FiraCode-Regular.ttf",
            bold_path="fonts/FiraCode-Bold.ttf"
        )
    
        self.manager.preload_fonts([
        {'name': 'pixelify', 'point_size': 32, 'style': 'bold'},
        {'name': 'pixelify', 'point_size': 28, 'style': 'bold'},
        {'name': 'fira code', 'point_size': 28, 'style': 'bold'},
        {'name': 'fira code', 'point_size': 16, 'style': 'bold'},
        {'name': 'fira code', 'point_size': 14, 'style': 'bold'},
        {'name': 'fira code', 'point_size': 36, 'style': 'bold'}
    ])
    
        self.manager.get_theme().load_theme('theme/theme.json')
        self.state_manager = StateManager(self.manager)
        
        self.launch_townhall_selection()

    def launch_base_draw(self, _townHallLevel: int):
        if self.townHallLevel == -1: self.townHallLevel = _townHallLevel
        if not self.base:
            self.base = Base(self.townHallLevel)
        if self.townHallLevel != _townHallLevel:
            self.base = Base(_townHallLevel)
        self.townHallLevel = _townHallLevel

        self.state_manager.set_state(
            BaseDesignScreen(
                self.manager,
                self.base,
                back_callback=self.launch_townhall_selection,
                next_callback=self.launch_troop_selection,
                load_callback=self.update_base_callback
            )
        )

    def launch_troop_selection(self, _townHallLevel: int):
        if self.townHallLevel == -1: self.townHallLevel = _townHallLevel
        if not self.deck:
            self.deck = Deck(self.townHallLevel)
        if self.deck.townHallLevel != _townHallLevel:
            self.deck = Deck(_townHallLevel)
        self.townHallLevel = _townHallLevel

        self.state_manager.set_state(
            TroopSelectionScreen(
                self.deck,
                self.manager,
                # TODO: Add and implement the `back` and `next` call back function
                self.launch_base_draw,
                self.launch_attack_screen,
                self.update_deck_callback
            ))

    def launch_townhall_selection(self):
        self.state_manager.set_state(
            MainScreen(
                self.manager,
                self.launch_base_draw
            )
        )

    def launch_attack_screen(self):
        self.state_manager.set_state(
            AttackScreen(
                self.manager,
                self.base,
                self.deck,
                self.launch_troop_selection
            )
        )

    def update_base_callback(self, base: Base):
        self.base = base
        self.townHallLevel = self.base.townHallLevel

    def update_deck_callback(self, deck: Deck):
        self.deck = deck
        self.townHallLevel = self.deck.townHallLevel

    def run(self):
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.state_manager.handle_event(event)
                self.manager.process_events(event)

            self.state_manager.update(time_delta)
            self.manager.update(time_delta)

            self.window.fill((0, 0, 0))
            self.manager.draw_ui(self.window)
            self.state_manager.draw(self.window)

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.run()