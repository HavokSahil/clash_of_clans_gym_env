from GameEngine.troops import *
from GameEngine.structures import *
from GameEngine.base import *
from GameEngine.renderer import *

scene = SceneBase(town_hall_level=TownHall.LEVEL5)
viewer = SceneRenderer(scene)
viewer.run()

# print(Wall())
# print(Barrack())
# print(AllianceCastle())
# print(ArcherTower())
# print(WizardTower())
# print(GoldMine())
# print(ElixirPump())
# print(Wall())
# print(AllianceCastle())
