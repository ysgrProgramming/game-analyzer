from dataclasses import dataclass
from game_analyzer import State, Game, Solver
from typing import Literal
from problems.shiritori import CASE_LIST


@dataclass
class ShiritoriState(State):
    last: int


class Shiritori(Game):
    def __init__(self, words):
        self.words = words
        self.default_eval = 1
        self.init_state = ShiritoriState(last=-1)

    def find_next_states(self, state):
        if state.last == -1:
            for i in range(len(self.words)):
                state.last = i
                yield state
            state.last = -1
        else:
            buf = state.last
            for i in range(len(self.words)):
                if self.words[state.last][-3:] == self.words[i][:3]:
                    state.last = i
                    yield state
            state.last = buf

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        return None


def test_solver_by_shiritori():
    for case, ans_list in CASE_LIST:
        shiritori = Shiritori(**case)
        solver = Solver()
        result = solver.solve(shiritori)
        for i in range(len(shiritori.words)):
            ev, depth = result.state_to_params(ShiritoriState(i))
            assert ev == ans_list[i]
