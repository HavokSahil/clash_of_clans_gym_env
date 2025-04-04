from gymnasium.wrappers import FlattenObservation
from stable_baselines3 import PPO
from coc_env import WarzoneEnv
from warbase import Base
from deck import Deck
from stable_baselines3.common.vec_env import DummyVecEnv

# Create and initialize environment
base = Base(5)
deck = Deck(5)
base.fillRandomly()
deck.fillRandomly()

env = WarzoneEnv(townHallLevel=5, base=base, deck=deck, is_rendering=False)
env = FlattenObservation(env)
vec_env = DummyVecEnv([lambda: env])

# Train the model
model = PPO(
    "MlpPolicy",
    vec_env,
    verbose=1,
    tensorboard_log="./ppo_warzone_tensorboard/"
)

model.learn(total_timesteps=100_000)
model.save("ppo_warzone")

# Turn on rendering AFTER training
vec_env.envs[0].switch_render(True)

# Evaluation loop
obs = vec_env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = vec_env.step(action)
    vec_env.envs[0].render()
