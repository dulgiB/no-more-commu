import random

# 기본적인 전투의 뼈대
# 세부적인 시스템에 따라 이 오브젝트를 상속해서 오버라이드

class Character(object):
    def __init__(self, name, stats:dict) -> None:
        self.name = name
        self.stats = stats
        self.isActed = False

class Mob(object):
    def __init__(self, idx) -> None:
        self.idx = idx

class Skill(object):
    def __init__(self) -> None:
        pass

class BattleManager():
    def __init__(self) -> None:
        pass