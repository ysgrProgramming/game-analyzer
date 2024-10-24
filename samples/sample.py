from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterable
from typing import Literal
import numpy as np

import sys
import pypyjit


sys.setrecursionlimit(10**9)
pypyjit.set_param("max_unroll_recursion=-1")


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
        return ev - np.sign(ev)

    def next_eval(self, ev: int) -> int:
        if abs(ev) == self._max_depth:
            msg = "eval depth limit"
            raise ValueError(msg)
        return ev + np.sign(ev)

    def eval_to_params(self, ev: int) -> tuple[int, int]:
        result = np.sign(ev)
        dist = self._max_depth - np.abs(ev)
        return result, dist

    def params_to_eval(self, result: int, depth: int) -> int:
        if depth > self._max_depth:
            msg = "depth must be less than _max_depth"
            raise ValueError(msg)
        return (self._max_depth - depth) * result


@dataclass
class Result:
    hash_dict: dict[int, int]
    eval_list: list[int]
    max_depth: int
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


@dataclass
class Solver:
    max_depth: int = 10000
    _game: Game = None  # type: ignore
    _ep_conv: EvalParamsConverter = None  # type: ignore
    _hash_dict: dict[int, int] = field(default_factory=dict)
    _max_eval_list: list[int] = field(default_factory=list)
    _min_eval_list: list[int] = field(default_factory=list)
    _graph_inv: list[list[int]] = field(default_factory=list)
    _child_count_list: list[int] = field(default_factory=list)
    _depth_list: list[list[int]] = field(default_factory=lambda: [[]])

    def __post_init__(self):
        self._ep_conv = EvalParamsConverter(max_depth=self.max_depth)

    def solve(self, game: Game) -> Result:
        self._game = game
        init_idx = self._register_state(self._game.init_state)
        self._alphabeta_analyze(self._game.init_state, init_idx)
        self._retrograde_analyze()
        return Result(hash_dict=self._hash_dict, eval_list=self._min_eval_list, max_depth=self.max_depth)

    def _alphabeta_analyze(self, state: State, idx: int) -> tuple[int, int]:  # noqa: C901
        min_eval, max_eval = self._ep_conv.params_to_eval(-1, 1), self._ep_conv.params_to_eval(-1, 1)
        for next_state in self._game.find_next_states(state):
            next_hash = next_state.to_hash()
            if next_hash in self._hash_dict:
                next_idx = self._hash_dict[next_hash]
                next_min_eval, next_max_eval = self._min_eval_list[next_idx], self._max_eval_list[next_idx]
            else:
                next_idx = self._register_state(next_state)
                next_res = self._game.evaluate_state(next_state)
                if next_res is not None:
                    next_eval = self._ep_conv.params_to_eval(next_res, 0)
                    next_min_eval, next_max_eval = next_eval, next_eval
                    self._confirm_eval(next_idx, next_eval)
                else:
                    next_min_eval, next_max_eval = self._alphabeta_analyze(next_state, next_idx)
            min_eval = max(min_eval, -self._ep_conv.prev_eval(next_max_eval))
            max_eval = max(max_eval, -self._ep_conv.prev_eval(next_min_eval))
            self._min_eval_list[idx] = min_eval
            if not self._is_confirmed(next_idx):
                self._child_count_list[idx] += 1
                self._graph_inv[next_idx].append(idx)
        self._max_eval_list[idx] = max_eval
        if self._is_confirmed(idx):
            self._confirm_eval(idx, min_eval)
        else:
            self._pending_eval(idx)
        return min_eval, max_eval

    def _retrograde_analyze(self):  # noqa: C901
        for idx_list in self._depth_list[1:]:
            for idx in idx_list:
                if not self._is_confirmed(idx):
                    self._confirm_eval(idx, self._min_eval_list[idx])
        for idx in self._depth_list[0]:
            if not self._is_confirmed(idx):
                self._confirm_eval(idx, 0)

    def _register_state(self, state: State) -> int:
        idx = len(self._min_eval_list)
        min_hash = -1
        for mirror_state in self._game.find_mirror_states(state):
            state_hash: int = mirror_state.to_hash()  # type: ignore
            if state_hash in self._hash_dict and self._hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            self._hash_dict[state_hash] = idx
            min_hash = min(min_hash, state_hash)
        self._max_eval_list.append(self._ep_conv.params_to_eval(1, 1))
        self._min_eval_list.append(self._ep_conv.params_to_eval(-1, 1))
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _confirm_eval(self, idx: int, ev: int):
        self._min_eval_list[idx] = ev
        self._max_eval_list[idx] = ev
        prev_ev = self._ep_conv.prev_eval(ev)
        for prev_idx in self._graph_inv[idx]:
            if self._min_eval_list[prev_idx] < -prev_ev:
                self._min_eval_list[prev_idx] = -prev_ev
                self._pending_eval(prev_idx)
            self._max_eval_list[prev_idx] = max(self._max_eval_list[prev_idx], -prev_ev)
            self._child_count_list[prev_idx] -= 1
            if self._child_count_list[prev_idx] == 0:
                self._confirm_eval(prev_idx, prev_ev)
        self._graph_inv[idx] = []

    def _pending_eval(self, idx: int):
        res, depth = self._ep_conv.eval_to_params(self._min_eval_list[idx])
        if depth >= len(self._depth_list):
            self._depth_list.extend([[] for _ in range(depth - len(self._depth_list) + 1)])
        if res == 1:
            self._depth_list[depth].append(idx)
        else:
            self._depth_list[0].append(idx)

    def _is_confirmed(self, idx: int):
        return self._min_eval_list[idx] == self._max_eval_list[idx]


@dataclass
class Game(ABC):
    init_state: State
    default_eval: int = 0

    @abstractmethod
    def find_next_states(self, state: State) -> Iterable[State]:
        pass

    @abstractmethod
    def find_mirror_states(self, state: State) -> Iterable[State]:
        yield state

    @abstractmethod
    def evaluate_state(self, state: State) -> Literal[-1, 0, 1] | None:
        return None


class State:
    def to_hash(self):
        return hash(convert_object_to_hashable(self.__dict__))