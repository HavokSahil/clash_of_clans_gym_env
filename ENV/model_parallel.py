from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from gymnasium.wrappers import FlattenObservation
from coc_env import WarzoneEnv
from warbase import Base
from deck import Deck

# Number of parallel environments
NUM_ENVS = 8

# Function to create an environment instance
def make_env():
    def _init():
        base = Base(5)
        deck = Deck(5)
        base.fillRandomly()
        deck.fillRandomly()
        env = WarzoneEnv(townHallLevel=5, base=base, deck=deck, is_rendering=False)
        env = FlattenObservation(env)
        return env
    return _init

# Create parallel environments using SubprocVecEnv
vec_env = SubprocVecEnv([make_env() for _ in range(NUM_ENVS)])

# Optional: custom policy network
policy_kwargs = dict(
    net_arch=[256, 128],  # Smaller MLP, modify as needed
)

# Initialize PPO model
model = PPO(
    policy="MlpPolicy",
    env=vec_env,
    verbose=1,
    n_steps=4096,           # Bigger rollouts = better PPO updates
    batch_size=1024,
    device="cuda",          # "cuda" for GPU, "cpu" otherwise
    policy_kwargs=policy_kwargs,
    tensorboard_log="./ppo_warzone_tensorboard/"
)

# Train the model
model.learn(total_timesteps=1_000_000)
model.save("ppo_warzone")

# After training: turn on rendering for evaluation (just one env!)
# You can't render during SubprocVecEnv use, so we reload one env manually
base = Base(5)
deck = Deck(5)
base.fillRandomly()
deck.fillRandomly()
eval_env = WarzoneEnv(townHallLevel=5, base=base, deck=deck, is_rendering=True)
eval_env = FlattenObservation(eval_env)

obs = eval_env.reset()
done = False

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = eval_env.step(action)
    eval_env.render()
