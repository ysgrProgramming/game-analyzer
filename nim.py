import numpy as np
from analyzer import Analyzer

init_mat = np.array([10])
max_mat = np.array([11])

x_list = list(range(1, 4))
def next_func(mat):
    for x in x_list:
        put_mat = mat-x
        if put_mat[0] < 0: continue
        yield put_mat

an = Analyzer(init_mat, max_mat, next_func, default=-1)
print(an.week_solve())
