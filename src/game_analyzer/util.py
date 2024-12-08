from collections.abc import Hashable, Iterable


def convert_iterable_to_hashable(variable: Hashable | Iterable[Iterable | Hashable]) -> Hashable:
    if isinstance(variable, Hashable):
        return variable
    elif isinstance(variable, Iterable):  # noqa: RET505
        return tuple(convert_iterable_to_hashable(item) for item in variable)  # type: ignore
    else:
        msg = "cannot convert to hashable"
        raise TypeError(msg)


def convert_dict_to_hashable(dictionary: dict[str, Hashable | Iterable]):
    if not isinstance(dictionary, dict):
        msg = "type must be dict"
        raise TypeError(msg)
    return tuple(convert_iterable_to_hashable(v) for v in dictionary.values())


def convert_object_to_hashable(obj: Hashable | Iterable[Iterable | Hashable] | dict[str, Hashable | Iterable]):
    if isinstance(obj, dict):
        return convert_dict_to_hashable(obj)  # type: ignore
    return convert_iterable_to_hashable(obj)


class EvalParamsConverter:
    def __init__(self, max_depth=1000):
        self._max_depth = max_depth

    def prev_eval(self, ev: int) -> int:
        if abs(ev) == 1:
            msg = "eval depth limit"
            raise ValueError(msg)
        result = 1 if ev > 0 else (-1 if ev < 0 else 0)
        return ev - result

    def next_eval(self, ev: int) -> int:
        if abs(ev) == self._max_depth:
            msg = "eval depth limit"
            raise ValueError(msg)
        result = 1 if ev > 0 else (-1 if ev < 0 else 0)
        return ev + result

    def eval_to_params(self, ev: int) -> tuple[int, int]:
        result = 1 if ev > 0 else (-1 if ev < 0 else 0)
        dist = self._max_depth - abs(ev)
        return result, dist

    def params_to_eval(self, result: int, depth: int) -> int:
        if depth > self._max_depth:
            msg = "depth must be less than _max_depth"
            raise ValueError(msg)
        return (self._max_depth - depth) * result
