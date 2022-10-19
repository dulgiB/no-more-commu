from oauth2client.service_account import ServiceAccountCredentials
import gspread
from grapher import Grapher

# 시트를 읽고 쓰는 도우미 객체

SHEET_TITLE = "이곳에 시트 제목을 작성하세요"
LIST_SHEET_NAME = "목록"
FIELD_SHEET_NAME = "필드"
LOG_SHEET_NAME = "로그"

class SheetManager():
    def __init__(self) -> None:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
                 '{your JSON key file path}', scope)
        gc = gspread.authorize(credentials).open(SHEET_TITLE)

        self.list = gc.worksheet(LIST_SHEET_NAME)
        self.field = gc.worksheet(FIELD_SHEET_NAME)
        self.log = gc.worksheet(LOG_SHEET_NAME)
    
    # 시트에서 스탯 읽어오기

    # 시트 업데이트

    # 시트에 로그 작성하기

