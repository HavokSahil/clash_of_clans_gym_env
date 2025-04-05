import pygame
import pygame_gui

from GameObject.deck import Deck

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

        self.ui_elements = []

    def on_enter(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface: pygame.Surface):
        pass

    def clean_up(self):
        for elem in self.ui_elements:
            elem.kill()
        self.ui_elements = []