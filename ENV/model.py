from gymnasium.wrappers import FlattenObservation
from stable_baselines3 import PPO
from coc_env import WarzoneEnv
from GameObject.warbase import Base
from GameObject.deck import Deck
from stable_baselines3.common.vec_env import DummyVecEnv

# Create and initialize environment
townhall_level = 3

base = Base(townhall_level)
deck = Deck(townhall_level)
base.fillRandomly()
deck.fillRandomly()

env = WarzoneEnv(townHallLevel=townhall_level, base=base, deck=deck, is_rendering=False)
env = FlattenObservation(env)
vec_env = DummyVecEnv([lambda: env])

# Train the model
# model = PPO(
#     "MlpPolicy",
#     vec_env,
#     verbose=1,
#     tensorboard_log="./ppo_warzone_tensorboard/",
# )

model = PPO.load("ppo_warzone", env=vec_env)
# model.learn(total_timesteps=100_000)
# model.save("ppo_warzone")


raw_env = vec_env.envs[0]
while hasattr(raw_env, "env"):
    raw_env = raw_env.env

# Now you can call your custom method
raw_env.switch_render(True)

# Evaluation loop
obs = vec_env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = vec_env.step(action)
    vec_env.envs[0].render()
    
