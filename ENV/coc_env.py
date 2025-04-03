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
    def __init__(self, townHallLevel=1, base: Base = None, deck: Deck = None):
        super(WarzoneEnv, self).__init__()
        
        assert base is not None
        assert deck is not None

        self.base = base
        self.deck = deck

        self.townHallLevel = townHallLevel

        self.renderer = WarzoneRenderer()

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
        self.action_space = spaces.MultiDiscrete([45, 45, len(self.deck.get_deck_member_ids(self.warzone.deckSpace)) + 1])
        
        self.total_reward = 0
        self.steps = 0
        self.maxSteps = 900
 
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
        if deckID < len(self.deck.get_deck_member_ids(self.warzone.deckSpace)):
            self.warzone.deploy_troop(deckID, position=(y, x))
        
        self.warzone.update()
        reward = self.compute_reward()
        done = self.is_done()
        
        self.steps += 1
        # if self.steps >= self.maxSteps:
        #     done = True
        
        return {
            "base": self.warzone.baseSpace,
            "troops": self.warzone.troopSpace,
            "deck": self.warzone.deckSpace
        }, reward, done, False, {}
    
    def compute_reward(self):
        """ Computes reward based on damage dealt and buildings destroyed. """
        # damage_dealt = self.warzone.get_damage_dealt()
        # buildings_destroyed = self.warzone.get_buildings_destroyed()
        
        # reward = damage_dealt * 0.1 + buildings_destroyed * 10
        reward = 0
        self.total_reward += reward
        
        return reward

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
        # for y in range(self.warzone.troopSpace.shape[0]):
        #     if self.warzone.troopSpace[y, 0] == -1: continue
        #     for x in range(self.warzone.troopSpace.shape[1]):
        #         print(self.warzone.troopSpace[y, x], end=' ')
        #     print()

        # print()

        self.renderer.render(self.warzone.baseSpace, self.warzone.troopSpace, self.warzone.deckSpace, self.townHallLevel)


if __name__ == "__main__":

    base = Base(5)
    deck = Deck(5)

    base.fillRandomly()
    deck.fillRandomly()

    env = WarzoneEnv(townHallLevel=5, base=base, deck=deck)
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
