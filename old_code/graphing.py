import networkx as nx
import matplotlib.pyplot as plt
import scipy

# A(0), I(8): 1~7
# B(1), H(7): 1~9
# C(2), G(6): 1~11
# D(3), E(4), F(5): 1~13

# A1 = B2 = C3 = D4 = E4 = F4 = G3 = H2 = I1

graph = nx.Graph()

rows = "ABCDEFGHI"
rowLength = {"A": 7, "B": 9, "C": 11, "D": 13, "E": 13, "F": 13, "G": 11, "H": 9, "I": 7}


class WrongDirectionError(Exception):
    pass


def up(row, col):
    if row == 0:
        return "X"
    elif row <= 3:
        if col == 1 or col == rowLength[rows[row]]:
            return "X"
        return rows[row-1] + str(col-1)
    elif row >= 6:
        return rows[row-1] + str(col+1)
    else:
        return rows[row-1] + str(col)

def down(row, col):
    if row == 8:
        return "X"
    elif row >= 5:
        if col == 1 or col == rowLength[rows[row]]:
            return "X"
        return rows[row+1] + str(col-1)
    elif row <= 2:
        return rows[row+1] + str(col+1)
    else:
        return rows[row+1] + str(col)

def left(row, col):
    if col == 1:
        return "X"
    else:
        return rows[row] + str(col-1)

def right(row, col):
    if col == rowLength[rows[row]]:
        return "X"
    else:
        return rows[row] + str(col+1)


def findAdj(coordinate):
    row = rows.index(coordinate[0])
    col = int(coordinate[1:])
    ret = []

    U = up(row, col)
    D = down(row, col)
    L = left(row, col)
    R = right(row, col)

    for c in [U, D, L, R]:
        if c != "X":
            ret.append(c)

    return ret


def buildGraph():
    for i in rows:
        for j in range(rowLength[i]):
            graph.add_node(i + str(j + 1))

    for node in list(graph.nodes):
        adj = findAdj(node)
        for i in adj:
            graph.add_edge(node, i)

    return graph


if __name__ == '__main__':
    g = buildGraph()
    nx.draw_kamada_kawai(g)
    plt.show()