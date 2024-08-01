import numpy as np
from typing import Hashable, Iterable


def convert_iterable_to_hashable(variable: Hashable | Iterable[Iterable | Hashable]) -> Hashable:
    if isinstance(variable, Hashable):
        return variable
    elif isinstance(variable, Iterable):
        return tuple(convert_iterable_to_hashable(item) for item in variable)
    else:
        raise Exception("cannot convert to hashable")


def convert_dict_to_hashable(dictionary: dict[str, Hashable | Iterable]):
    if not isinstance(dictionary, dict):
        raise TypeError("type must be dict")
    keys = sorted(k for k in dictionary.keys() if not k.startswith("_"))
    variables = tuple(map(lambda k: convert_iterable_to_hashable(dictionary[k]), keys))
    return variables


def convert_object_to_hashable(object: Hashable | Iterable[Iterable | Hashable] | dict[str, Hashable | Iterable]):
    if isinstance(object, dict):
        return convert_dict_to_hashable(object)
    else:
        return convert_iterable_to_hashable(object)

    
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
    