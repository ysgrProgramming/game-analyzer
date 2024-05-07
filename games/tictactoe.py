from base import Game
import numpy as np
from collections.abc import Generator

class TicTacToe(Game):
    size: int
    require: int
    range_of_elements = (0, 3)
    default_eval = 0
    
    def __init__(self, size: int, require: int):
        self.size = size
        self.require = require
        self.init_state = np.zeros((self.size, self.size), dtype=int)
        
    def find_mirror_states(self, state):
        flip_state = np.flip(state)
        for i in range(4):
            yield(np.rot90(state, i))
            yield(np.rot90(flip_state, i))

    def evaluate_state(self, state):
        for i in range(4):
            rot_state = np.rot90(state, i)
            if rot_state[0][0] == rot_state[1][1] == rot_state[2][2] == 2:
                return -1
            elif rot_state[0][0] == rot_state[0][1] == rot_state[0][2] == 2:
                return -1
            elif rot_state[1][0] == rot_state[1][1] == rot_state[1][2] == 2:
                return -1
        if np.count_nonzero(rot_state == 0) == 0: return 0
        return None

    def find_put_states(self, state):
        for y in range(3):
            for x in range(3):
                if state[y][x] == 0:
                    put_state = state.copy()
                    put_state[y][x] = 1
                    yield put_state

    def find_reverse_state(self, state):
        rev_state = state*2%3
        return rev_state
    
    def find_next_states(self, state):
        for put_state in self.find_put_states(state):
            next_state = self.find_reverse_state(put_state)
            yield next_state

tictactoe = TicTacToe(size=5, require=4)
print(tictactoe.init_state)