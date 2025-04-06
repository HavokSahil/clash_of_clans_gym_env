import threading
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
import os

class TrainingProgressCallback(BaseCallback):
    def __init__(self, ui_callback, total_timesteps, should_stop_fn, verbose=0):
        super().__init__(verbose)
        self.ui_callback = ui_callback
        self.total_timesteps = total_timesteps
        self.should_stop_fn = should_stop_fn 

    def _on_step(self) -> bool:
        progress = self.n_calls / self.total_timesteps
        self.ui_callback(progress)

        if self.should_stop_fn():
            print("Stopping training due to external signal.")
            return False
        return True

def train_ppo_model(env, total_timesteps, progress_callback, finish_callback, stop_event: threading.Event):
    def run():
        model_path = "ppo_model.zip"

        if os.path.exists(model_path):
            print("Loading existing PPO model...")
            model = PPO.load(model_path, env=env)
        else:
            print("Creating a new PPO model...")
            model = PPO(
                "MultiInputPolicy",
                env,
                verbose=1,
                tensorboard_log="./ppo_warzone_tensorboard/",
            )

        callback = TrainingProgressCallback(
            ui_callback=progress_callback,
            total_timesteps=total_timesteps,
            should_stop_fn=lambda: stop_event.is_set()
        )

        model.learn(total_timesteps=total_timesteps, callback=callback)
        model.save(model_path)
        print("Model saved to", model_path)

        finish_callback()

    thread = threading.Thread(target=run)
    thread.start()
    return thread

