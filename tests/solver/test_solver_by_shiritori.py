from dataclasses import dataclass
from game_analyzer import State, Game, Solver
from typing import Literal
from problems.shiritori import CASE_LIST


@dataclass(slots=True)
class ShiritoriState(State):
    last: Literal[-1] | str


class Shiritori(Game):
    def __init__(self, words):
        self.words = words
        self.word_dict = {}
        for word in words:
            if word[:3] not in self.word_dict:
                self.word_dict[word[:3]] = set()
            self.word_dict[word[:3]].add(word[-3:])
        self.default_eval = 1
        self.init_state = ShiritoriState(last=-1)

    def find_next_states(self, state):
        if state.last == -1:
            for word in self.words:
                yield ShiritoriState(last=word[-3:])
        else:
            if state.last not in self.word_dict:
                return
            for word in self.word_dict[state.last]:
                yield ShiritoriState(last=word)

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
