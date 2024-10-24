from game_analyzer import State, Game, Solver
from dataclasses import dataclass


@dataclass
class NimState(State):
    stones: int


class Nim(Game):
    def __init__(self, init_stones, hands):
        self.init_state = NimState(stones=init_stones)
        self.hands = hands

    def find_next_states(self, state):
        for i in range(1, self.hands + 1):
            if state.stones - i < 0:
                break
            yield NimState(stones=state.stones - i)

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        if state.stones == 0:
            return -1
        return None


if __name__ == "__main__":
    nim = Nim(init_stones=10**4, hands=3)
    solver = Solver(max_depth=10**9)
    result = solver.solve(nim)
    print(result.state_to_params(nim.init_state))
