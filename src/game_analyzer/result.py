import pickle
from array import array
from dataclasses import dataclass
from pathlib import Path

from game_analyzer import State


@dataclass
class Result:
    hash_dict: dict[int, int]
    zobrist_map: dict
    eval_list: array
    depth_list: array
    sgg_time: float
    ra_time: float

    def state_to_params(self, state: State) -> tuple[int, int] | None:
        state.set_zobrist_map(self.zobrist_map)
        state_hash = state.to_hash()
        if state_hash in self.hash_dict:
            idx = self.hash_dict[state_hash]
            return self.eval_list[idx], self.depth_list[idx]
        return None

    def dump(self, path: Path) -> None:
        pickle.dump(self, Path.open(path, "wb"))

    @classmethod
    def load(cls, path: Path) -> "Result":
        return pickle.load(Path.open(path, "rb"))  # noqa: S301
