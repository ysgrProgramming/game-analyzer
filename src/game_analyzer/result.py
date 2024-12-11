from array import array
from dataclasses import dataclass

from game_analyzer import State


def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


@dataclass
class Result:
    hash_dict: dict[int, int]
    eval_list: array
    depth_list: array
    sgg_time: float
    ra_time: float

    def state_to_params(self, state: State) -> tuple[int, int] | None:
        state_hash = state.to_hash()
        if state_hash in self.hash_dict:
            idx = self.hash_dict[state_hash]
            return self.eval_list[idx], self.depth_list[idx]
        return None
