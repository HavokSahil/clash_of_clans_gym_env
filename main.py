from GameEngine.troops import *
from GameEngine.structures import *
from GameEngine.base import *
from GameEngine.renderer import *

scene = SceneBase(town_hall_level=TownHall.LEVEL5)

for i in range(5):
    scene.place_troop(Giant(Giant.LEVEL5), 20, 30 + i)

for i in range(5):
    scene.place_troop(Archer(Archer.LEVEL5), 40, 30 + i)

viewer = SceneRenderer(scene)
viewer.run()