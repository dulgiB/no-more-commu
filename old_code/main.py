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

json_file_name = 'FILE-NAME-HERE.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

spreadsheet_url = 'https://docs.google.com/spreadsheets/d/18sgyGibbfw77rHc2mLPSvOgRQc6GVtyYv8YW5Mhbj_A/edit?usp=sharing'
# 관련 가이드는 이 링크 참조
# https://yurimkoo.github.io/python/2019/07/20/link-with-googlesheets-for-Python.html

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
    turnCount = 1

    print("1단계: 인원 배치")
    for name in battleField.info.keys():
        if credentials.access_token_expired:
            gc.login()
        location = input(name + "의 위치는? >> ").upper()
        if location == "X":
            continue
        battleField.add(name, battleField.info[name][0], battleField.info[name][2], battleField.info[name][1], battleField.info[name][3], location)
        if battleField.info[name][0] == "네볼":
            config.nevolStart += battleField.info[name][2]
        else:
            config.arkStart += battleField.info[name][2]

    print("2단계: 전투 개시 멘션 대기")
    while True:
        try:
            checkMentions(api, last_id, battleField)
            logging.info("Waiting...")
            time.sleep(30)
        except StartBattle:
            print("전투 개시 멘션 확인. 위치 공개 트윗을 올려주세요.")
            break

    print("3단계: 턴 진행")
    isCurrentNevol = bool(input("선공은? >> ") == "네볼")

    while turnCount <= 4:
        try:
            for char in battleField.characters.keys():
                battleField.update(char, 0, doneFlag=False)

            c = current[int(isCurrentNevol)]  # 네볼 or 아크
            logging.info("{}턴: {}의 선공".format(turnCount, c))
            now = datetime.datetime.now()
            end = now + datetime.timedelta(minutes=10)
            api.update_status("| {}턴: 선공 - {}\n\n{}시 {}분 {}초까지 본 트윗의 답글로 커맨드를 전송해 주세요.".format(turnCount, c, end.hour, end.minute, end.second))

            try:
                for i in range(20):
                    if credentials.access_token_expired:
                        gc.login()
                    logging.info("대기 중...")
                    last_id = checkMentions(api, last_id, battleField)
                    time.sleep(30)
                last_id = checkMentions(api, last_id, battleField)
            except EndTurn:
                pass

            logging.info("{}턴: 선공 커맨드 입력 종료".format(turnCount))
            api.update_status("| 선공 커맨드 입력 종료. 잠시 후 최종 위치를 공개합니다. ({})".format(datetime.datetime.now().strftime("%m-%d %H:%M:%S")))

            # 도약 정산
            if len(config.leapTuples) != 0:
                for i in config.leapTuples:
                    battleField.leaperSkill(i[0], i[1])
            config.leapTuples = []

            print("스테이터스를 업데이트합니다. 잠시만 기다리세요...")
            battleField.updateList(status)

            input("위치 공개 트윗 전송 후 엔터를 입력하세요!")

            c = current[int(not isCurrentNevol)]  # 네볼 or 아크
            logging.info("{}턴: {}의 후공".format(turnCount, c))
            now = datetime.datetime.now()
            end = now + datetime.timedelta(minutes=10)
            api.update_status("| {}턴: 후공 - {}\n\n{}시 {}분 {}초까지 본 트윗의 답글로 커맨드를 전송해 주세요.".format(turnCount, c, end.hour, end.minute, end.second))

            last_id = api.mentions_timeline()[0].id + 1
            try:
                for i in range(20):
                    if credentials.access_token_expired:
                        gc.login()
                    logging.info("대기 중...")
                    last_id = checkMentions(api, last_id, battleField)
                    time.sleep(30)
                last_id = checkMentions(api, last_id, battleField)
            except EndTurn:
                pass
            logging.info("{}턴: 후공 커맨드 입력 종료".format(turnCount))
            api.update_status("| 후공 커맨드 입력 종료. 잠시 후 최종 위치를 공개합니다. ({})".format(datetime.datetime.now().strftime("%m-%d %H:%M:%S")))

            # 도약 정산은 여기서
            if len(config.leapTuples) != 0:
                for i in config.leapTuples:
                    battleField.leaperSkill(i[0], i[1])
            config.leapTuples = []

            print("스테이터스를 업데이트합니다. 잠시만 기다리세요...")
            battleField.updateList(status)

            input("위치 공개 트윗 전송 후 엔터를 입력하세요!")

            turnCount += 1

        except EndBattle:
            api.update_status("| 승리 조건 달성으로 전투를 종료합니다. 잠시 후 전투 결과를 공지합니다.")
            break

        if turnCount == 5:
            api.update_status("| 턴 경과로 전투를 종료합니다. 잠시 후 전투 결과를 공지합니다.")

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

