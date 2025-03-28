from GameEngine.troops import *
from GameEngine.structures import *
from GameEngine.base import *
from GameEngine.renderer import *

scene = SceneBase(town_hall_level=TownHall.LEVEL5)
townhall = TownHall(TownHall.LEVEL5)
castle = AllianceCastle(AllianceCastle.LEVEL3)

scene.place_building(townhall, 10, 10)
scene.place_building(castle, 7, 11)
scene.place_building(Cannon(Cannon.LEVEL5), 15, 10)

scene.place_building(GoldMine(GoldMine.LEVEL6), 5, 5)
scene.place_building(GoldMine(GoldMine.LEVEL4), 30, 30)

for i in range(15):
    scene.place_building(Wall(Wall.LEVEL1), 6 + i, 9)
    scene.place_building(Wall(Wall.LEVEL1), 6 + i, 14)

for i in range(9, 15):
    scene.place_building(Wall(Wall.LEVEL1), 20, i)
    scene.place_building(Wall(Wall.LEVEL1), 6, i)

scene.place_troop(Giant(Giant.LEVEL5), 15, 25)
balloon = Balloon(Balloon.LEVEL3)
scene.place_troop(balloon, 20, 20)

scene.place_troop(Barbarian(Barbarian.LEVEL6), 25, 35)
scene.place_troop(Wizard(Wizard.LEVEL4), 25, 25)
scene.place_troop(Goblin(Goblin.LEVEL2), 25, 35)
viewer = SceneRenderer(scene)
viewer.run()