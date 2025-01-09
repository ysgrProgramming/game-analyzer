from dataclasses import dataclass
from game_analyzer import State, Game, Solver
from typing import Literal
from problems.shiritori import CASE_LIST


@dataclass
class ShiritoriState(State):
    last: Literal[-1] | str


class Shiritori(Game):
    def __init__(self, words):
        self.words = words
        self.word_dict = {}
        for word in words:
            if word not in self.word_dict:
                self.word_dict[word[:3]] = set()
            self.word_dict[word[:3]].add(word[-3:])
        self.default_eval = 1
        self.init_state = ShiritoriState(last=-1)

    def find_next_states(self, state):
        if state.last == -1:
            for i in range(len(self.words)):
                state.last = self.words[i][-3:]
                yield state
            state.last = -1
        else:
            buf = state.last
            if state.last not in self.word_dict:
                return
            for word in self.word_dict[state.last]:
                state.last = word
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
            ev, depth = result.state_to_params(ShiritoriState(shiritori.words[i][-3:]))
            assert ev == ans_list[i]


test_solver_by_shiritori()
