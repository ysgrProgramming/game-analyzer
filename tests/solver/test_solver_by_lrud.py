from dataclasses import dataclass
from game_analyzer import State, Game, Solver
from typing import Literal
from problems.lrud import CASE_LIST


@dataclass(slots=True)
class LRUDState(State):
    r: int
    c: int
    step: int
    turn: Literal[0, 1]


class LRUD(Game):
    move_dict = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}

    def __init__(self, h, w, init_cd, s_list, t_list, max_step):
        self.h = h
        self.w = w
        self.s_list = s_list
        self.t_list = t_list
        self.max_step = max_step
        r, c = init_cd

        self.init_state = LRUDState(r=r, c=c, step=0, turn=0)

    def find_next_states(self, state):
        r, c, step, turn = state.r, state.c, state.step, state.turn
        if turn == 0:
            d = [(0, 0), self.move_dict[self.s_list[step]]]
            for dr, dc in d:
                yield LRUDState(r=r + dr, c=c + dc, step=step, turn=1)
        else:
            d = [(0, 0), self.move_dict[self.t_list[step]]]
            for dr, dc in d:
                yield LRUDState(r=r + dr, c=c + dc, step=step + 1, turn=0)

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        r, c, step, turn = state.r, state.c, state.step, state.turn
        if not self._is_on_board(r, c):
            if turn == 0:
                return 1
            return -1
        if step == self.max_step:
            if turn == 0:
                return -1
            return 1
        return None

    def _is_on_board(self, r, c):
        return 1 <= r <= self.h and 1 <= c <= self.w


def test_solver_by_lrud():
    for case, ans in CASE_LIST:
        lrud = LRUD(**case)
        solver = Solver()
        result = solver.solve(lrud)
        ev, depth = result.state_to_params(lrud.init_state)
        assert ev == ans
