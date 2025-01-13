from game_analyzer import HashState, Game, Solver
from dataclasses import dataclass
from tests.solver.problems.stones import CASE_LIST


@dataclass
class StonesState(HashState):
    stones: int


class Stones(Game):
    def __init__(self, init_stones, hand_list):
        self.init_state = StonesState(stones=init_stones)
        self.hand_list = hand_list
        self.default_eval = -1

    def find_next_states(self, state):
        for hand in self.hand_list:
            state.stones -= hand
            if state.stones >= 0:
                yield state
            state.stones += hand

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        return None


def test_solver_by_stones():
    for case, ans in CASE_LIST:
        stones = Stones(**case)
        solver = Solver()
        result = solver.solve(stones)
        ev, depth = result.state_to_params(stones.init_state)
        assert ev == ans
