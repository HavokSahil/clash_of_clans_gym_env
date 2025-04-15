pyinstaller --onefile --name app \
--add-data "images:images" \
--add-data "fonts:fonts" \
--add-data "theme:theme" \
--add-data "ppo_model.zip:models" \
--add-data "$(python3 -c 'import os, stable_baselines3; print(os.path.join(os.path.dirname(stable_baselines3.__file__), "version.txt"))')":stable_baselines3 \
app.py

