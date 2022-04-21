import tweepy
import logging
import random
import time
import datetime
import csv
import pandas as pd
import config
from Field import *

auth = tweepy.OAuthHandler("USER_TOKEN", "USER_TOKEN_SECRER")
auth.set_access_token("ACCESS_TOKEN",
                      "ACCESS_TOKEN_SECRET")

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
logging.basicConfig(format="", level=logging.INFO)


class StartBattle(Exception):
    pass


class EndTurn(Exception):
    pass


class EndBattle(Exception):
    pass


def parseCommand(text: str):
    cmd = ""
    for i in range(text.index("[") + 1, text.index("]")):
        cmd += text[i]
    parsed = cmd.split("/")
    return [p.strip() for p in parsed]


def writeLog(id, logList):  # [name, command, target, roll]
    timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csvLog = open(config.logfile, 'a')
    csvLog.write("{},{}\n".format(timeStamp, id))
    log.insert_row([timeStamp] + logList, 2)


def executeCommand(text, userid, tweetid, f: Field):
    parsedList = parseCommand(text)
    name = f.IDmap[userid]
    character = f.getChar(name)
    initLocation = character.location
    try:
        if len(parsedList) == 1:  # 이동
            f.move(name, parsedList[0].upper())
            writeLog(tweetid, [name, "이동", "", ""])
        elif len(parsedList) == 2:  # 이동 후 공격
            f.move(name, parsedList[0].upper())
            # target = f.findName(parsedList[1])
            # targetC = f.getChar(target)
            roll = f.attack_raid(name)
            writeLog(tweetid, [name, "이동/공격", "오메가", roll])
            # if targetC.hp == 0:
            #    f.clear(targetC.location)
        elif len(parsedList) == 3:  # 스킬
            if character.pos == "탐색":
                f.move(name, parsedList[0].upper())
                names = parsedList[2].split(",")
                for i in names:
                    target = f.findName(i.strip())
                    roll = f.skill(name, target)
                    writeLog(tweetid, [name, "스킬", target, roll])
            else:
                target = f.findName(parsedList[2])
                if character.pos == "가속" or character.pos == "도약":
                    f.move(name, parsedList[0].upper())
                roll = f.skill(name, target)
                writeLog(tweetid, [name, "스킬", target, roll])
                # if f.getChar(target).hp == 0:
                #    f.clear(f.getChar(target).location)
        else:
            pass
        f.update(name, 0, doneFlag=True)
    except AlreadyOccupiedError:
        api.update_status(
            "| 해당 위치에는 현재 다른 캐릭터가 위치하고 있어 이동할 수 없습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                              random.randint(1, 100),
                                                                                              random.randint(1, 100)),
            in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except StaticPointError:
        api.update_status(
            "| 해당 위치는 고정점이므로 이동할 수 없습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                 random.randint(1, 100),
                                                                                 random.randint(1, 100)),
            in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except NoPathError:
        api.update_status("| 해당 위치로 이동 가능한 경로가 없습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                             random.randint(1, 100),
                                                                                             random.randint(1, 100)),
                          in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except NotReachableError:
        api.update_status("| 해당 위치는 이동력을 벗어나는 거리에 있습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                                random.randint(1, 100),
                                                                                                random.randint(1, 100)),
                          in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except OutOfRangeError:
        f.move(name, initLocation)
        api.update_status("| 공격 대상의 위치가 사정거리를 벗어납니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                             random.randint(1, 100),
                                                                                             random.randint(1, 100)),
                          in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except SkillCountError:
        f.move(name, initLocation)
        api.update_status("| 사용 가능한 스킬 횟수를 전부 소진하였습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                               random.randint(1, 100),
                                                                                               random.randint(1, 100)),
                          in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except WrongTargetError:
        f.move(name, initLocation)
        api.update_status("| 지정한 대상을 찾을 수 없습니다. 확인 후 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                        random.randint(1, 100),
                                                                                        random.randint(1, 100)),
                          in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])
    except gspread.exceptions.APIError:
        f.move(name, initLocation)
        api.update_status(
            "| 내부 오류로 커맨드가 전달되지 않았습니다. 죄송합니다. 답글로 동일 커맨드를 재전송해 주세요.\n\n{}.{}.{}".format(random.randint(1, 100),
                                                                                        random.randint(1, 100),
                                                                                        random.randint(1, 100)),
            in_reply_to_status_id=tweetid, auto_populate_reply_metadata=True)
        writeLog(tweetid, [name, "오류", "", ""])


def systemCommand(text, tweetid):  # 진행 계정 커맨드: [전투 개시], [턴 종료], [전투 종료]
    text = parseCommand(text)[0]
    if text == '전투 개시':
        writeLog(tweetid, ["진행", "전투 개시", "", ""])
        raise StartBattle
    elif text == '턴 종료':
        writeLog(tweetid, ["진행", "턴 종료", "", ""])
        raise EndTurn
    elif text == '전투 종료':
        writeLog(tweetid, ["진행", "전투 종료", "", ""])
        raise EndBattle
    else:
        print("잘못된 커맨드입니다")


def readIDs(filename):
    columns = ["timestamp", "tweetID"]
    df = pd.read_csv(filename, names=columns)
    return df.tweetID.to_list()


def checkMentions(API: tweepy.API, last_id, f: Field):
    new_id = last_id
    for tweet in reversed(API.mentions_timeline(since_id=last_id)):
        new_id = max(tweet.id, new_id)

        if new_id not in readIDs(config.logfile):
            logging.info("[{}] Received command from @{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                 tweet.user.screen_name))
            if tweet.user.id == config.storyID:
                systemCommand(tweet.text, tweet.id)
            elif tweet.user.id in list(f.IDmap.keys()):
                executeCommand(tweet.text, tweet.user.id, tweet.id, f)
            else:
                pass
            API.create_favorite(tweet.id)
            time.sleep(2)
    return new_id


def checkReach(API: tweepy.API, last_id, f: Field):
    new_id = last_id
    for tweet in reversed(API.mentions_timeline(since_id=last_id)):
        new_id = max(tweet.id, new_id)

        if new_id not in readIDs(config.logfile):
            logging.info("[{}] Received reach from @{}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                               tweet.user.screen_name))
            API.create_favorite(tweet.id)
            time.sleep(2)
    return new_id


if __name__ == '__main__':
    last_id = api.mentions_timeline()[0].id + 1
    battleField = Field(field)

    while True:
        try:
            logging.info("Waiting...")
            last_id = checkReach(api, last_id, battleField)
            time.sleep(30)
        except:
            pass
