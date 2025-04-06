from gymnasium.wrappers import FlattenObservation
from stable_baselines3 import PPO
from coc_env import WarzoneEnv
from GameObject.warbase import Base
from GameObject.deck import Deck

import pickle

# Create and initialize environment
townhall_level = 1
base_filename = "th1base.pkl"
deck_filename = "th1deck.pkl"

with open(base_filename, 'rb') as f:
    base = pickle.load(f)

with open(deck_filename, "rb") as f:
    deck = pickle.load(f)


env = WarzoneEnv(townHallLevel=townhall_level, base=base, deck=deck, is_rendering=False)
# env = FlattenObservation(env)

# # Train the model
# model = PPO(
#     "MultiInputPolicy",
#     env,
#     verbose=1,
#     tensorboard_log="./ppo_warzone_tensorboard/",
# )

model = PPO.load("ppo_model", env=env)
# model.learn(total_timesteps=100_000)
# model.save("ppo_model")

# Now you can call your custom method
env.switch_render(True)

# Evaluation loop
obs, _ = env.reset()
done = False
while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    
