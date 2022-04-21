from graphing import *
from Character import *
import gspread
import config
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    ]

json_file_name = 'forward-subject-264411-e3129bbf3ae2.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1eeqbn1wm36zsYHprJxdFhgkHSpm4RkKu9839O5do-yw/edit?usp=sharing'

doc = gc.open_by_url(spreadsheet_url)
field = doc.worksheet('필드')
stat = doc.worksheet('스테이터스')
log = doc.worksheet('로그')

locationMap = {"A1":"E3:E5", "A2":"F3:F5", "A3":"G3:G5", "A4":"H3:H5", "A5":"I3:I5", "A6":"J3:J5", "A7":"K3:K5",
               "B1":"D7:D9", "B2":"E7:E9", "B3":"F7:F9", "B4":"G7:G9", "B5":"H7:H9", "B6":"I7:I9", "B7":"J7:J9", "B8":"K7:K9", "B9":"L7:L9",
               "C1":"C11:C13", "C2":"D11:D13", "C3":"E11:E13", "C4":"F11:F13", "C5":"G11:G13", "C6":"H11:H13", "C7":"I11:I13", "C8":"J11:J13", "C9":"K11:K13", "C10":"L11:L13", "C11":"M11:M13",
               "D1":"B15:B17", "D2":"C15:C17", "D3":"D15:D17", "D4":"E15:E17", "D5":"F15:F17", "D6":"G15:G17", "D7":"H15:H17", "D8":"I15:I17", "D9":"J15:J17", "D10":"K15:K17", "D11":"L15:L17", "D12":"M15:M17", "D13":"N15:N17",
               "E1":"B19:B21", "E2":"C19:C21", "E3":"D19:D21", "E4":"E19:E21", "E5":"F19:F21", "E6":"G19:G21", "E7":"H19:H21", "E8":"I19:I21", "E9":"J19:J21", "E10":"K19:K21", "E11":"L19:L21", "E12":"M19:M21", "E13":"N19:N21",
               "F1":"B23:B25", "F2":"C23:C25", "F3":"D23:D25", "F4":"E23:E25", "F5":"F23:F25", "F6":"G23:G25", "F7":"H23:H25", "F8":"I23:I25", "F9":"J23:J25", "F10":"K23:K25", "F11":"L23:L25", "F12":"M23:M25", "F13":"N23:N25",
               "G1":"C27:C29", "G2":"D27:D29", "G3":"E27:E29", "G4":"F27:F29", "G5":"G27:G29", "G6":"H27:H29", "G7":"I27:I29", "G8":"J27:J29", "G9":"K27:K29", "G10":"L27:L29", "G11":"M27:M29",
               "H1":"D31:D33", "H2":"E31:E33", "H3":"F31:F33", "H4":"G31:G33", "H5":"H31:H33", "H6":"I31:I33", "H7":"J31:J33", "H8":"K31:K33", "H9":"L31:L33",
               "I1":"E35:E37", "I2":"F35:F37", "I3":"G35:G37", "I4":"H35:H37", "I5":"I35:I37", "I6":"J35:J37", "I7":"K35:K37"}
done = ["미행동", "행동완료"]
blockedGoals = [["D13", "E13", "F13"], ["D1", "E1", "F1"]]    # 0: 네볼, 1: 아크

# 레이드 한정 변수
blockedPoint = ["C4", "E4", "G4", "C8", "E10", "G8"]


def ID_dict():
    ID = stat.col_values(1)[1:]
    name = stat.col_values(2)[1:]
    d = {}

    for i in range(len(ID)):
        try:
            d[int(ID[i])] = name[i]
        except:
            pass
    return d

def makeDict():
    name = stat.col_values(2)[1:]
    side = stat.col_values(3)[1:]
    position = stat.col_values(4)[1:]
    HP = stat.col_values(5)[1:]
    skillCount = stat.col_values(6)[1:]
    d = {}

    for n in range(len(name)):
        try:
            d[name[n]] = [side[n], position[n], int(HP[n]), int(skillCount[n])]
        except:
            pass

    return d


class AlreadyOccupiedError(Exception):
    pass

class NoPathError(Exception):
    pass

class NotReachableError(Exception):
    pass

class OutOfRangeError(Exception):
    pass

class SkillCountError(Exception):
    pass

class WrongTargetError(Exception):
    pass

class StaticPointError(Exception):
    pass


class Field(object):
    def __init__(self, sheet):
        self.field = sheet
        self.IDmap = ID_dict()   # ID: 'name'
        self.info = makeDict()   # name: [진영, 포지션, 체력, 잔여 스킬 횟수] - 초기 변수
        self.occupied = []    # keeps track of occupied cells
        self.characters = {}  # maps character name to Character object
        self.g = buildGraph()

    def place(self, dest, character):
        cells = self.field.range(locationMap[dest])

        cells[0].value = "{} ({})".format(character.name, character.hp)
        cells[1].value = character.pos
        cells[2].value = done[int(character.done)]

        character.location = dest
        self.occupied.append(dest)
        self.field.update_cells(cells)

    def add(self, name, side, HP, position, skillCount, dest):
        char = Character(name, side, HP, position, skillCount)
        self.place(dest, char)
        self.characters[name] = char

    def getChar(self, name):
        return self.characters[name]

    def findName(self, text):
        for i in self.info.keys():
            if i.find(text) != -1:
                return i
        raise WrongTargetError

    def update(self, name, damage, doneFlag=False):
        char = self.getChar(name)
        cells = self.field.range(locationMap[char.location])

        char.hp = max(char.hp - damage, 0)
        char.done = doneFlag

        cells[0].value = "{} ({})".format(char.name, char.hp)
        cells[1].value = char.pos
        cells[2].value = done[int(doneFlag)]
        self.field.update_cells(cells)

    def updateList(self, status):
        cells = status.range("B2:F23")
        updateList = []

        for i in range(22):
            idx = i*5
            try:
                char = self.getChar(cells[idx].value)
            except:
                l = [cells[idx+j].value for j in range(5)]
                updateList.append(l)
                continue

            updateList.append([char.name, char.side, char.pos, char.hp, char.skill])

        status.update("B2:F23", updateList)

    def clear(self, dest):
        cells = self.field.range(locationMap[dest])
        for cell in cells:
            cell.value = ""

        self.occupied.remove(dest)
        self.field.update_cells(cells)

    def checkPath(self, path):
        for i in path[1:]:
            if i in self.occupied or i in blockedPoint:
                return False
        return True

    def movable(self, source, target):
        ret = False

        for path in [p for p in nx.all_shortest_paths(self.g, source, target)]:
            if self.checkPath(path):
                ret = True
                break
        return ret

    def reachable(self, name, dest, move=False):
        character = self.getChar(name)
        dist = len(nx.shortest_path(self.g, character.location, dest))-1

        if move:
            if character.seekFlag:
                character.seekFlag = False
                return dist <= character.stats[1] + 2
            return dist <= character.stats[1]
        return dist <= character.stats[2]

    def checkOmegaRange(self, c: Character):
        minLength = 100
        if c.side == "네볼":
            for dest in config.staticReal:
                temp = len(nx.shortest_path(self.g, c.location, dest))
                if minLength > temp:
                    minLength = temp
        else:
            for dest in config.staticVirt:
                temp = len(nx.shortest_path(self.g, c.location, dest))
                if minLength > temp:
                    minLength = temp
        return minLength-1 <= c.stats[2]

    def move(self, name, dest):
        character = self.getChar(name)

        if dest in blockedPoint:
            raise StaticPointError
        if dest != character.location and dest in self.occupied:
            raise AlreadyOccupiedError
        if not self.reachable(name, dest, move=True):
            raise NotReachableError

        start = character.location

        if self.movable(start, dest):
            self.clear(start)
            self.place(dest, character)
        else:
            raise NoPathError

    def attack(self, name, targetName):
        character = self.getChar(name)
        target = self.getChar(targetName)

        if self.reachable(character.name, target.location):
            roll = character.attack()
            self.update(targetName, roll, doneFlag=target.done)
            self.update(name, 0, doneFlag=True)
            return roll
        else:
            raise OutOfRangeError

    def attack_raid(self, name):
        character = self.getChar(name)

        if self.checkOmegaRange(character):
            roll = character.attack()
            config.bossHP -= roll
            self.update(name, 0, doneFlag=True)
            return roll
        else:
            raise OutOfRangeError

    def skill(self, name, targetName):
        char = self.getChar(name)
        if char.skill == 0:
            raise SkillCountError
        char.skill -= 1

        if char.pos == "저격":
            return self.sniperSkill(char, targetName)
            
        elif char.pos == "탐색":
            self.seekerSkill(targetName)
            
        elif char.pos == "도약":
            # config.leapTuples.append((char, targetName))
            self.leaperSkill(char, targetName)
            
        else:
            return self.accelSkill(char, targetName)

    def sniperSkill(self, c, targetName):
        roll = round(c.attack() * 1.6)  # 1.3
        # self.update(targetName, roll, doneFlag=self.getChar(targetName).done)
        config.bossHP -= roll
        self.update(c.name, 0, doneFlag=True)
        return roll

    def seekerSkill(self, targetName):
        target = self.getChar(targetName)
        target.seekFlag = True
        return

    def leaperSkill(self, c, targetName):
        target = self.getChar(targetName)

        A = c.location
        B = target.location

        self.clear(A)
        self.clear(B)

        self.place(B, c)
        self.place(A, target)
        return

    def accelSkill(self, c, targetName):
        if targetName == "오메가":
            if self.checkOmegaRange(c.location):
                roll = round(c.attack() * 1.2)
                config.bossHP -= roll
                return roll
        else:
            target = self.getChar(targetName)
            if len(nx.shortest_path(self.g, c.location, target.location)) != 2:
                return -1
            else:
                A = c.location
                B = target.location
                dest = ""
                funcs = ["self.accelUp", "self.accelDown", "self.accelLeft", "self.accelRight"]
                for f in funcs:
                    try:
                        dest = eval(f + "(A, B, {})".format(int(target.side == "아크")))
                    except WrongDirectionError:
                        pass

                if dest == "":
                    raise OutOfRangeError
                else:
                    roll = round(c.attack() * 1.2)
                    target.updateHP(roll)
                    self.place(dest, target)
                    self.clear(B)
            return roll

    def accelUp(self, A, B, s):
        Arow = rows.index(A[0])
        Acol = int(A[1])

        if up(Arow, Acol) != B:
            raise WrongDirectionError

        dest = B
        temp = B
        for i in range(3):
            r = rows.index(dest[0])
            c = int(dest[1])
            dest = up(r, c)
            if dest == "X" or dest in self.occupied or dest in blockedPoint:  # blockedGoals[s]
                return temp
            temp = dest
        return dest

    def accelDown(self, A, B, s):
        Arow = rows.index(A[0])
        Acol = int(A[1])

        if down(Arow, Acol) != B:
            raise WrongDirectionError

        dest = B
        temp = B
        for i in range(3):
            r = rows.index(dest[0])
            c = int(dest[1])
            dest = down(r, c)
            if dest == "X" or dest in self.occupied or dest in blockedPoint:  # blockedGoals[s]
                return temp
            temp = dest
        return dest

    def accelLeft(self, A, B, s):
        Arow = rows.index(A[0])
        Acol = int(A[1])

        if left(Arow, Acol) != B:
            raise WrongDirectionError

        dest = B
        temp = B
        for i in range(3):
            r = rows.index(dest[0])
            c = int(dest[1])
            dest = left(r, c)
            if dest == "X" or dest in self.occupied or dest in blockedPoint:  # blockedGoals[s]
                return temp
            temp = dest
        return dest

    def accelRight(self, A, B, s):
        Arow = rows.index(A[0])
        Acol = int(A[1])

        if right(Arow, Acol) != B:
            raise WrongDirectionError

        dest = B
        temp = B
        for i in range(3):
            r = rows.index(dest[0])
            c = int(dest[1])
            dest = right(r, c)
            if dest == "X" or dest in self.occupied or dest in blockedPoint:  # blockedGoals[s]
                return temp
            temp = dest
        return dest


if __name__ == '__main__':
    pass
