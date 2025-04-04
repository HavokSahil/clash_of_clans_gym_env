from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from gymnasium.wrappers import FlattenObservation

from coc_env import WarzoneEnv
from warbase import Base
from deck import Deck

# Initialize environment
base = Base(5)
deck = Deck(5)
base.fillRandomly()
deck.fillRandomly()

env = WarzoneEnv(townHallLevel=5, base=base, deck=deck, is_rendering=False)
env = FlattenObservation(env)
vec_env = DummyVecEnv([lambda: env])

# Train DQN model
model = DQN(
    "MlpPolicy",
    vec_env,
    verbose=1,
    learning_rate=1e-4,
    buffer_size=50000,           # Experience replay buffer
    learning_starts=1000,        # Start learning after collecting some steps
    batch_size=32,
    tau=1.0,                     # Soft update factor
    train_freq=4,                # How often to train the model
    target_update_interval=1000,
    exploration_fraction=0.1,    # Exploration schedule
    exploration_final_eps=0.01,
    tensorboard_log="./dqn_warzone_tensorboard/"
)

model.learn(total_timesteps=100_000)
model.save("dqn_warzone")

