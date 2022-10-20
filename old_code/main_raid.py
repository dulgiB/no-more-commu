import gspread
import config
from Character import *
from Field import *
from tweetFuncs import *
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
log = doc.worksheet('로그')
status = doc.worksheet('스테이터스')

current = ["아크", "네볼"]


if __name__ == '__main__':
    print("전투 다이스 시작!!! 오늘도 죽지 말고 파이팅합시다")
    print("여기서 잠깐! 스킬횟수는 업데이트했는지 체력은 갱신했는지 확인하세요")
    input("문제없다면 엔터")

    battleField = Field(field)
    for i in ["E3:K5", "D7:L9", "C11:M13", "B15:N17", "B19:N21", "B23:N25", "C27:M29", "D31:L33", "E35:K37"]:
        cells = field.range(i)
        for cell in cells:
            cell.value = ""

        field.update_cells(cells)

    last_id = api.mentions_timeline()[0].id + 1
    turnCount = 3

    print("1단계: 인원 배치")
    for name in battleField.info.keys():
        if credentials.access_token_expired:
            gc.login()
        location = input(name + "의 위치는? >> ").upper()
        if location == "X":
            continue
        battleField.add(name, battleField.info[name][0], battleField.info[name][2], battleField.info[name][1], battleField.info[name][3], location)

    print("3단계: 턴 진행")

    while True:
        try:
            if turnCount == 3:
                while True:
                    target = input(">> ")
                    if target == "끝":
                        break
                    else:
                        roll = 0
                        targetName = battleField.findName(target)
                        for i in range(dice):
                            roll += random.randint(1, 6)
                        battleField.update(targetName, roll)
                        writeLog(1234, ["오메가", "공격", targetName, roll])

            for char in battleField.characters.keys():
                battleField.update(char, 0, doneFlag=False)

            logging.info("{}턴 개시".format(turnCount))
            config.staticReal = []
            config.staticVirt = []

            print("이번 턴의 <현실> 고정점 입력")
            for i in range(3):
                config.staticReal.append(input(">> ").upper())
            print("이번 턴의 <가상> 고정점 입력")
            for i in range(3):
                config.staticVirt.append(input(">> ").upper())

            input("고정점 재정렬 후 위치를 공개하세요. 완료되었을 시 엔터를 눌러주세요.")

            input("기믹 힌트 연출 진행 후 엔터를 눌러주세요!")

            now = datetime.datetime.now()
            end = now + datetime.timedelta(minutes=15)
            api.update_status("| {}턴\n\n{}시 {}분 {}초까지 본 트윗의 답글로 커맨드를 전송해 주세요.".format(turnCount, end.hour, end.minute, end.second))

            try:
                for i in range(40):
                    if credentials.access_token_expired:
                        gc.login()
                    logging.info("대기 중...")
                    last_id = checkMentions(api, last_id, battleField)
                    time.sleep(22)
                last_id = checkMentions(api, last_id, battleField)
            except EndTurn:
                pass

            logging.info("{}턴: 커맨드 입력 종료".format(turnCount))
            api.update_status("| 커맨드 입력 종료. 잠시 후 해당 턴의 공격 범위 및 최종 위치를 공개합니다. ({})".format(datetime.datetime.now().strftime("%m-%d %H:%M:%S")))

            print("스테이터스를 업데이트합니다. 잠시만 기다리세요...")
            battleField.updateList(status)

            input("기믹 공개 후 엔터를 입력하세요!")



            dice = int(input("이번 턴은 ?d6 >> "))
            print("공격 범위 안에 든 캐릭터들의 이름을 입력하세요!")

            while True:
                target = input(">> ")
                if target == "끝":
                    break
                else:
                    roll = 0
                    targetName = battleField.findName(target)
                    for i in range(dice):
                        roll += random.randint(1, 6)
                    battleField.update(targetName, roll)
                    writeLog(1234, ["오메가", "공격", targetName, roll])

            print("스테이터스를 업데이트합니다. 잠시만 기다리세요...")
            battleField.updateList(status)

            input("최종 위치 공개 후 엔터를 입력하세요!")
            print("잔여 체력: {}".format(config.bossHP))
            turnCount += 1

        except EndBattle:
            api.update_status("| 전투를 종료합니다. 잠시 후 전투 결과를 공지합니다.")
            break

    arriveWin = input("목적지 달성으로 전투가 종료됐나요? (맞음: 승리 진영명, 틀림: x) >> ")
    if arriveWin.upper() == "X":
        nevolSum = 0
        arkSum = 0

        for name in battleField.characters.keys():
            char = battleField.getChar(name)
            if char.side == "네볼" and char.name != "서노을":
                nevolSum += char.hp
            elif char.side == "아크" and char.name != "판도라 엘렌":
                arkSum += char.hp

        if nevolSum == arkSum:
            api.update_status("| 전투 결과\n\n네볼 잔여 체력: {}\n아크 잔여 체력: {}\n\n>> 무승부".format(nevolSum, arkSum))
        else:
            didNevolWin = int(nevolSum > arkSum)
            api.update_status("| 전투 결과\n\n네볼 잔여 체력: {}\n아크 잔여 체력: {}\n\n>> {} 승".format(nevolSum, arkSum, current[didNevolWin]))

    else:
        api.update_status("| 전투 결과\n\n>> 목적지 이동 달성으로 {} 승리".format(arriveWin))

    input("고생하셨습니다... 가서 종료지문 올리셈 이제")

