from dataclasses import dataclass
from array import array
from game_analyzer.util import EvalParamsConverter
from game_analyzer import State

@dataclass
class Result:
    hash_dict: dict[int, int]
    eval_list: array
    max_depth: int
    sgg_time: float
    ra_time: float
    _ep_conv: EvalParamsConverter = None  # type: ignore

    def __post_init__(self):
        self._ep_conv = EvalParamsConverter(self.max_depth)

    def state_to_params(self, state: State) -> tuple[int, int] | None:
        state_hash = state.to_hash()
        if state_hash in self.hash_dict:
            idx = self.hash_dict[state_hash]
            ev = self.eval_list[idx]
            res, depth = self._ep_conv.eval_to_params(ev)
            return res, depth
        return None
