import random


# 공격력, 이동력, 사정거리
statsDict = {"저격": [5, 1, 3], "탐색": [3, 2, 1],
             "도약": [3, 2, 2], "가속": [4, 3, 1]}


class Character(object):

    def __init__(self, name, side, HP, position, skillCount):
        self.name = name
        self.side = side
        self.hp = HP
        self.pos = position
        self.skill = skillCount
        self.stats = statsDict[self.pos]
        self.location = None
        self.seekFlag = False
        self.done = False

    def updateHP(self, diff):
        self.hp -= diff

    def attack(self):
        roll = 0
        for i in range(self.stats[0]):
            roll += random.randint(1, 6)
        return roll
