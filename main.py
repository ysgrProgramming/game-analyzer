import numpy as np
from analyzer import Analyzer

init_mat = np.array([
    [1, 0, 0],
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

def next_func(mat):
    mat = mat*2%3
    for y in range(3):
        for x in range(3):
            if mat[y][x] == 0:
                new_mat = mat.copy()
                new_mat[y][x] = 1
                yield new_mat

an = Analyzer(init_mat, max_mat, next_func, sym_func, end_func)
an.construct_game_graph()
an.make_tree()
print(an.mat_to_min_hash(init_mat))
print(an.example(0))