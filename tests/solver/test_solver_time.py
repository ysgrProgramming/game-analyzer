from game_analyzer import State, Game, Solver
from dataclasses import dataclass
from tests.solver.problems.stones import CASE_LIST


@dataclass(slots=True)
class StonesState(State):
    stones: int


class Stones(Game):
    def __init__(self, init_stones, hand_list):
        self.init_state = StonesState(stones=init_stones)
        self.hand_list = hand_list
        self.default_eval = -1

    def find_next_states(self, state):
        for hand in self.hand_list:
            next_stones = state.stones - hand
            if next_stones >= 0:
                yield StonesState(stones=next_stones)

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        return None


# 0.02 s
def test_evaluate_state_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    for i in range(100000):
        state = StonesState(stones=i)
        stones.evaluate_state(state)


# 0.03 s
def test_find_mirror_state_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    for i in range(100000):
        state = StonesState(stones=i)
        for s in stones.find_mirror_states(state):
            pass


# 1.54 s
def test_find_next_states_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    for i in range(100000):
        state = StonesState(stones=i)
        for s in stones.find_next_states(state):
            pass  # s.to_hash()


# 4.47 s
def test_find_next_states_with_to_hash_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    for i in range(100000):
        state = StonesState(stones=i)
        for s in stones.find_next_states(state):
            s.to_hash()


# 4.48 s
def test_game_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    for i in range(100000):
        state = StonesState(stones=i)
        for s in stones.find_next_states(state):
            s.to_hash()
        stones.evaluate_state(state)
        stones.find_mirror_states(state)


# 7.38 s
def test_solver_time():
    stones = Stones(init_stones=100000, hand_list=list(range(1, 100)))
    solver = Solver()
    result = solver.solve(stones)
    ev, depth = result.state_to_params(stones.init_state)
