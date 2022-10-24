import random
from enum import Enum

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
    # 스킬은 네 종류
    SkillType = Enum("SkillType", "SNIPE ACCEL SEEK LEAP")

    def __init__(self, skillType:SkillType) -> None:
        self.skillType = skillType
    
    def snipeSkill(self):
        return
    
    def snipeSkill(self):
        return
    
    def snipeSkill(self):
        return
    
    def snipeSkill(self):
        return
    
    def execute(self):
        match self.skillType:
            case self.SkillType.SNIPE:
                self.snipeSkill()
            case self.SkillType.ACCEL:
                return
            case self.SkillType.SEEK:
                return
            case self.SkillType.LEAP:
                pass
            case _:
                return

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