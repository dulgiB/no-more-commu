from bidict import bidict

# 시트상의 마스에서 상하좌우 관계와 이동 가능 여부, 최단거리 등을
# 빠르게 구하기 위한 보조 코드

ALPHA_LIST = "ABCDEFGHIJKLMNOPQRTUVWXYZ"

class Grapher():
    def __init__(self, offsets:list, lengths:list) -> None:
        self.nodes = bidict()
        self.maxRow = len(offsets)

        # offsets: row마다 앞에 몇 칸씩 비어 있는지
        # lengths: row의 길이
        if len(offsets) != len(lengths): raise ValueError
        for i in range(len(offsets)):
            offset = offsets[i]
            for j in range(lengths[i]):
                nodeName = ALPHA_LIST[i] + str(j+1)
                self.nodes[(i+1, offset+j+1)] = nodeName  

    def up(self, cell: str) -> str:
        row, col = self.nodes.inverse[cell]
        try:
            return self.nodes[(row-1, col)]
        except KeyError:
            return "X"
    
    def down(self, cell: str) -> str:
        row, col = self.nodes.inverse[cell]
        try:
            return self.nodes[(row+1, col)]
        except KeyError:
            return "X"
    
    def left(self, cell: str) -> str:
        row, col = self.nodes.inverse[cell]
        try:
            return self.nodes[(row, col-1)]
        except KeyError:
            return "X"
    
    def right(self, cell: str) -> str:
        row, col = self.nodes.inverse[cell]
        try:
            return self.nodes[(row, col+1)]
        except KeyError:
            return "X"
