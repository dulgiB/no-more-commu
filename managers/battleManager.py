import random

# 기본적인 전투의 뼈대
# 세부적인 시스템에 따라 이 오브젝트를 상속해서 오버라이드

class Character(object):
    # 기본적인 캐릭터 클래스
    def __init__(self, name, stats:dict) -> None:
        self.name = name
        self.stats = stats
        self.isActed = False

class Mob(object):
    # PvE 시스템을 위한 몹 클래스
    # 전투 시스템에 따라 오버라이드해 사용한다.
    def __init__(self, idx) -> None:
        self.idx = idx

class Skill(object):
    # 복잡한 스킬 구현을 위한 스킬 클래스
    # 스킬 레벨, 스킬 효과, 사용 가능 횟수 등을 유동적으로 기록할 수 있다.
    def __init__(self) -> None:
        pass

class BattleManager():
    def __init__(self) -> None:
        self.characters = {}
        self.mobs = {}

    def getCharacterByName(self, name):
        try:
            return self.characters[name]
        except ValueError:
            return None
    
    def getMobByIdx(self, idx):
        try:
            return self.mobs[idx]
        except ValueError:
            return None
    
    def nDx(self, n, x):
        sum = 0
        for i in range(n):
            sum += random.randint(1, x)
        return sum