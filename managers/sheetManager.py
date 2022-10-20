from oauth2client.service_account import ServiceAccountCredentials
from enum import Enum
import gspread
from grapher import Grapher
import pandas as pd

# 시트를 읽고 쓰는 도우미 객체

SHEET_TITLE = "이곳에 시트 제목을 작성하세요"
LIST_SHEET_NAME = "목록"
FIELD_SHEET_NAME = "필드"
LOG_SHEET_NAME = "로그"

Presets = Enum('Presets', 'RECTANGULAR TRIANGULAR RHOMBUS')

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

        self.fieldMap = None
    
    def setFieldMap(self, rows, cols, preset:Presets=Presets.RECTANGULAR,
                     custom:tuple=None):
        if custom:
            self.fieldMap = Grapher(custom[0], custom[1])
        else:
            offsets, lengths = self.fieldPresets(rows, cols, preset)
    
    def fieldPresets(self, rows, cols, preset:Presets):
        if preset == Presets.RECTANGULAR:
            return [0 for i in range(rows)], [cols for i in range(rows)]
        else:
            return [], []
    
    # 시트에서 스탯 읽어오기
    def readCharacterData(self):
        pass

    # 시트 업데이트
    def updateCharacterData(self, data: pd.DataFrame):
        pass

    # 시트에 로그 작성하기
    def writeLog(self, data: pd.DataFrame):
        pass

