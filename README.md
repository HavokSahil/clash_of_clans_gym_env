# Clash of Clans Gymnasium Environment

A custom OpenAI Gym environment and Pygame GUI for simulating Clash of Clans–style attack mechanics, combined with a Proximal Policy Optimization (PPO) agent (via Stable-Baselines3) to learn optimal attacking strategies.

---

## 🚀 Project Overview

* **Environment**: A Gym-compatible environment (`WarzoneEnv`) that models base layouts, troop deployment, and reward functions for RL.
* **GUI**: A Pygame + pygame\_gui application (`app.py`) with screens for:

  * Base design
  * Troop selection
  * Attack simulation (where the agent plays)
* **Agent**: A PPO-based reinforcement learning agent implemented in `model.py` using Stable-Baselines3.

---

## 📂 Repository Structure

```plaintext
├── app.py                   # Main Pygame application entrypoint
├── model.py                 # RL agent (PPO) training & loading
├── requirements.txt         # Python dependencies
├── GameObject/              # Base & troop data models
├── ui_/                     # All GUI screens (Main, BaseDesign, TroopSelection, Attack)
├── utils/                   # Utility functions (resource_path, etc.)
└── agents/                  # (Optional) future folder for additional algorithms
```

---

## ⚙️ Installation

1. Clone this repo:

   ```bash
   git clone https://github.com/your-org/ClashGymEnv.git
   cd ClashGymEnv
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS / Linux
   venv\Scripts\activate.bat   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 📈 Training the Agent

1. Open `model.py` and configure your hyperparameters (learning rate, timesteps, etc.).

2. Run the training script:

   ```bash
   python model.py --train --timesteps 1000000
   ```

3. After training completes, a file `ppo_model.zip` (or similar) will be saved in the project root.

---

## ▶️ Running the GUI App

With a trained model in place, launch the Pygame application:

```bash
python app.py
```

1. **Main Screen**: Select your Town Hall level.
2. **Base Design**: Lay out defenses and buildings.
3. **Troop Selection**: Choose your deck composition.
4. **Attack Simulation**: Watch the PPO agent deploy troops and execute its learned strategy.

---

## 📚 Adding New Algorithms

* Create a new agent file in `agents/` (e.g., `q_learning.py`).
* Implement an `Agent` class with methods:

  * `select_action(state)`
  * `train(env, episodes)`
  * `save(path)` / `load(path)`
* In `ui_attack_screen.py`, import and instantiate your agent alongside the existing PPO agent.

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

* [OpenAI Gym](https://gym.openai.com/)
* [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)
* [Pygame](https://www.pygame.org/)
* [pygame\_gui](https://pygame-gui.readthedocs.io/)
