import numpy as np
from analyzer import Analyzer

init_mat = np.array([
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
])
max_mat = np.array([
    [3, 3, 3],
    [3, 3, 3],
    [3, 3, 3]
])

def sym_func(mat):
    flip_mat = np.flip(mat)
    for i in range(4):
        yield(np.rot90(mat, i))
        yield(np.rot90(flip_mat, i))

def end_func(mat):
    for i in range(4):
        rot_mat = np.rot90(mat, i)
        if rot_mat[0][0] == rot_mat[1][1] == rot_mat[2][2] == 2:
            return -1
        elif rot_mat[0][0] == rot_mat[0][1] == rot_mat[0][2] == 2:
            return -1
        elif rot_mat[1][0] == rot_mat[1][1] == rot_mat[1][2] == 2:
            return -1
    if np.count_nonzero(rot_mat == 0) == 0: return 0
    return None

def put_func(mat):
    for y in range(3):
        for x in range(3):
            if mat[y][x] == 0:
                put_mat = mat.copy()
                put_mat[y][x] = 1
                yield put_mat

def rev_func(mat):
    rev_mat = mat*2%3
    return rev_mat

def next_func(mat):
    for put_mat in put_func(mat):
        next_mat = rev_func(put_mat)
        yield next_mat

an = Analyzer(init_mat, max_mat, next_func, sym_func, end_func)
an.construct_game_graph()
an.solve_game_graph()

for mat in an.list_example(init_mat):
    dist, judge = an.mat_to_status(mat)
    print(dist, judge)
    print(mat)