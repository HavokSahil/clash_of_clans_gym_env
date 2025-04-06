# env_register.py
from gymnasium.envs.registration import register

register(
    id='Warzone-v0',
    entry_point='coc_env:WarzoneEnv',  # Update this!
    kwargs={
        "townHallLevel": 1,
        "base": None,
        "deck": None,
        "is_rendering": True
    }
)
