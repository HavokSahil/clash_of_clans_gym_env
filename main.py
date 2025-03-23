from GameEngine.troops import *
from GameEngine.structures import *

barbarian = Barbarian(Barbarian.LEVEL3)
archer = Archer(Archer.LEVEL1)
goblin = Goblin(Goblin.LEVEL7)
giant = Giant(Giant.LEVEL6)
wall_breaker = WallBreaker(WallBreaker.LEVEL1)
balloon = Balloon()
# print(
#     barbarian,
#     archer,
#     goblin,
#     giant,
#     wall_breaker,
#     balloon,
#     sep='\n'*2)


mortar = Mortar(Mortar.LEVEL3)
cannon = Cannon(Cannon.LEVEL1)
archerTower = ArcherTower(ArcherTower.LEVEL4)
wizardTower = WizardTower(WizardTower.LEVEL5)
townhall = TownHall(TownHall.LEVEL5)
wall = Wall(Wall.LEVEL4)

print(
    mortar,
    cannon,
    archerTower,
    wizardTower,
    townhall,
    wall,
    sep="\n"*2
)