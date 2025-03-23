from GameEngine.troops import *
from GameEngine.structures import *
from GameEngine.base import *
from GameEngine.renderer import *

scene = SceneBase()
townhall = TownHall(TownHall.LEVEL5)
castle = AllianceCastle(AllianceCastle.LEVEL3)

scene.place_building(townhall, 10, 10)
scene.place_building(castle, 11, 7)
scene.place_building(Cannon(Cannon.LEVEL5), 10, 15)

for i in range(10):
    scene.place_building(Wall(Wall.LEVEL2), 9, 6 + i)
    scene.place_building(Wall(Wall.LEVEL4), 14, 6 + i)

scene.place_troop(WallBreaker(WallBreaker.LEVEL3), 20, 10)
scene.place_troop(Balloon(Balloon.LEVEL5), 20, 13)

viewer = SceneRenderer(scene)
viewer.run()