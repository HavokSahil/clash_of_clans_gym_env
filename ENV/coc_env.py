from buildings import BaseBuilding
from typing import List, Tuple
from warbase import Base
from deck import Deck
from warzone import Warzone
from renderer import WarzoneRenderer

import gymnasium as gym
from gymnasium import spaces
import numpy as np

class WarzoneEnv(gym.Env):
    def __init__(self, townHallLevel=1, base: Base = None, deck: Deck = None, is_rendering: bool = True):
        super(WarzoneEnv, self).__init__()
        
        assert base is not None
        assert deck is not None

        self.base = base
        self.deck = deck

        self.townHallLevel = townHallLevel

        self.is_rendering = is_rendering
        self.renderer = WarzoneRenderer() if self.is_rendering else None

        self.warzone = Warzone(
            baseSpace=self.base.getStateSpace(),
            troopSpace=self.deck.getUnplacedTroopSpace(),
            deckSpace=self.deck.getStateSpace()
        )

        # Define observation space (Base + Deck + Troops)
        self.observation_space = spaces.Dict({
            "base": spaces.Box(low=-1, high=10000, shape=self.warzone.baseSpace.shape, dtype=np.int32),
            "troops": spaces.Box(low=-1, high=1000, shape=self.warzone.troopSpace.shape, dtype=np.int32),
            "deck": spaces.Box(low=0, high=1000, shape=self.warzone.deckSpace.shape, dtype=np.int32),
        })

        # Define action space (Deploy troops at (y, x) from a category)
        _height, _width, _ = self.warzone.baseSpace.shape
        self.action_space = spaces.MultiDiscrete([_height, _width, len(self.deck.get_deck_member_ids(self.warzone.deckSpace)) + 1])
        
        self.total_reward = 0
        self.steps = 0
        self.maxSteps = 900

    def switch_render(self, flag):
        if flag:
            self.renderer = WarzoneRenderer()
            self.is_rendering = True
            return
        
        self.renderer.clean()
        self.renderer = None
        self.is_rendering = False
        
 
    def reset(self, seed=None, options=None):
        """ Resets the environment for a new episode. """
        super().reset(seed=seed)

        self.base.clear()
        self.deck.clear()

        self.base.fillRandomly()
        self.deck.fillRandomly()
        
        self.warzone = Warzone(
            baseSpace=self.base.getStateSpace(),
            troopSpace=self.deck.getUnplacedTroopSpace(),
            deckSpace=self.deck.getStateSpace()
        )

        self.total_reward = 0
        self.steps = 0

        return {
            "base": self.warzone.baseSpace,
            "troops": self.warzone.troopSpace,
            "deck": self.warzone.deckSpace
        }, {}

    def step(self, action):
        """
        Executes one step in the environment.
        `action` is a tuple (y, x, troop_category)
        """
        y, x, deckID = action
        self.warzone.deploy_troop(deckID, position=(y, x))
        self.warzone.update()

        reward = self.compute_reward()
        done = self.is_done()

        self.steps += 1

        return {
            "base": self.warzone.baseSpace,
            "troops": self.warzone.troopSpace,
            "deck": self.warzone.deckSpace
        }, reward, done, False, {}
    
    def compute_reward(self):
        """ Computes reward based on damage dealt and buildings destroyed. """
        return self.warzone.get_reward()

    def is_done(self):
        """ Checks if the episode is over (all troops deployed or all buildings destroyed). """
        return self.warzone.did_end()
    
    def get_valid_actions(self):
        """
        Returns a list of valid (y, x, troop_category) actions.
        This ensures we don't select an already deployed troop or invalid position.
        """
        valid_actions = []
        for deckID in range(len(self.deck.get_deck_member_ids(self.warzone.deckSpace))):
            if not self.warzone.is_troop_deployed(deckID):
                for y in range(45):
                    for x in range(45):
                        if self.warzone.is_valid_deployment(y, x):
                            valid_actions.append((y, x, deckID))
        return valid_actions
    
    def render(self, mode='human'):
        """ Renders the environment. """
        if self.is_rendering:
            self.renderer.render(
                self.warzone.baseSpace,
                self.warzone.troopSpace,
                self.warzone.deckSpace, 
                self.townHallLevel,
                destruction_percentage=self.warzone.destruction_percentage,
                stars=self.warzone.stars,
                loot_gold=self.warzone.loot_gold,
                loot_elixir=self.warzone.loot_elixir,
                total_gold=self.warzone.total_gold,
                total_elixir=self.warzone.total_elixir,
                steps=self.warzone.timestep,
                total_steps=self.warzone.maxtimestep
            )


if __name__ == "__main__":

    base = Base(3)
    deck = Deck(3)

    base.fillRandomly()
    deck.fillRandomly()

    env = WarzoneEnv(townHallLevel=3, base=base, deck=deck)
    # Reset the environment
    obs, info = env.reset()
    # Run a simple loop
    while True:  # Run 100 timesteps
        action = env.action_space.sample()  # Random action
        obs, reward, done, truncated, info = env.step(action)
        env.render()  # Render if needed
        if done or truncated:
            break

    env.close()
