# Project: Clash of Clans Attack AI

![output](https://github.com/user-attachments/assets/ff410b9a-4537-45ae-aaf0-df9721cc29d6)


## Overview:
---------
Currently this is a simple Python-based scene visualization system built using Pygame. It allows placing and rendering structures (buildings) and units (troops) on a 2D grid-based map.

# Directory Structure:
--------------------
- `base.py`        : Core logic for map, buildings, and troop placement.
- `renderer.py`    : Visual rendering of the scene using Pygame.
- `structures.py`  : Definitions for different buildings/structures.
- `troops.py`      : Definitions for different troop types.
- `README.txt`     : This file.

## Dependencies:
- Python 3.x
- Pygame
- NumPy

## Install requirements:
---------------------
Make sure to install the necessary libraries before running the project:

    pip install pygame numpy

## File Details:
-------------

### 1. base.py
-----------
Defines the `SceneBase` class that maintains the grid and manages placement/removal of buildings and troops. 
Key methods:
- place_building(building, x, y)
- remove_building(building)
- place_troop(troop, x, y)
- remove_troop(troop)

### 2. renderer.py
--------------
Handles drawing the current state of the scene using Pygame.
- `SceneRenderer` class loads images, renders the background, buildings, troops, and grid.
- Use `.run()` to start the visual loop.

### 3. structures.py
----------------
Defines building types derived from `BaseStructure`. Each building has:
- Width and height in tiles
- Method `.get_image_path()` returning path to image file

Example buildings:
- TownHall
- GoldMine
- Barracks

### 4. troops.py
------------
Defines troop types derived from `TroopBase`. Each troop has:
- Movement speed
- Image path

Example troops:
- Barbarian
- Archer
- Wizard

## How to Use:
-----------
1. Initialize a `SceneBase`.
2. Create buildings/troops.
3. Place them on the map using `place_building` / `place_troop`.
4. Create a `SceneRenderer` with the scene and call `.run()`.

## Example usage:
--------------
```python
scene = SceneBase()
hall = TownHall()
scene.place_building(hall, 10, 10)

warrior = Warrior()
scene.place_troop(warrior, 12, 12)

renderer = SceneRenderer(scene)
renderer.run()
