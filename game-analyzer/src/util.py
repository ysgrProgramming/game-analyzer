import numpy as np
from typing import Hashable, Iterable


def convert_iterable_to_hashable(variable: Hashable | Iterable[Iterable | Hashable]) -> Hashable:
    if isinstance(variable, Hashable):
        return variable
    elif isinstance(variable, Iterable):
        return tuple(convert_iterable_to_hashable(item) for item in variable) # type: ignore
    else:
        raise Exception("cannot convert to hashable")

def convert_statedict_to_hashable(dictionary: dict[str, Hashable | Iterable]):
    keys = sorted(k for k in dictionary.keys() if not k.startswith("_"))
    variables = tuple(map(lambda k: convert_iterable_to_hashable(dictionary[k]), keys))
    return variables
        
class StateHashConverter:
    def __init__(self, shape: tuple, range_of_elements: tuple[int, int]):
        self.shape = shape
        self.range_of_elements = range_of_elements
        elements = np.prod(shape)
        range_size = range_of_elements[1] - range_of_elements[0]
        self.max_hash = range_size**elements
        x = np.arange(elements)
        self._higher_base = (range_size**(x+1)).reshape(shape)
        self._lower_base = (range_size**x).reshape(shape)
    
    def hash_to_state(self, hash: int) -> np.ndarray:
        state = hash % self._higher_base // self._lower_base
        return state

    def state_to_hash(self, state: np.ndarray) -> int:
        hash = np.sum(state * self._lower_base)
        return hash
    
class EvalParamsConverter:
    def __init__(self, max_depth=1000):
        self._max_depth = max_depth
    
    def next_eval(self, eval: int) -> int:
        if abs(eval) == 1: raise Exception("eval depth limit")
        return eval - ((eval > 0) - (eval < 0))
    
    def eval_to_params(self, eval: int) -> tuple[int, int]:
        result = np.sign(eval)
        dist = self._max_depth - np.abs(eval)
        return result, dist
    
    def params_to_eval(self, result: int, depth: int) -> int:
        if depth > self._max_depth: raise Exception("depth must be less than _max_depth")
        eval = (self._max_depth - depth) * result
        return eval
    