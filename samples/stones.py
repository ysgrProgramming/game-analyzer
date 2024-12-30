from __future__ import annotations  # noqa: INP001

import random
import sys
import time
from abc import ABC, abstractmethod
from array import array
from collections.abc import Callable, Hashable, Iterable, MutableSequence
from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import ClassVar, Literal

import pypyjit

pypyjit.set_param("max_unroll_recursion=-1")
sys.setrecursionlimit(10**7)


class HashArray(MutableSequence):
    __hash__ = None  # type: ignore

    def __init__(
        self,
        array: MutableSequence,
        callback: Callable[[int], None] | None = None,
        digest_map: dict | None = None,
        bit_size: int = 60,
    ):
        if digest_map is None:
            digest_map = {}
        if isinstance(array, HashArray):
            self._inner = array._inner  # noqa: SLF001
        else:
            self._inner = array
        self._callback = callback
        self._digest_map = digest_map
        self._bit_size = bit_size
        self._digest: int = 0

        for i in range(len(self)):
            value = self._inner[i]
            self._digest_value(i, value)

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index):
        return self._inner[index]

    def __setitem__(self, index, value):
        if index < 0:
            index += len(self._inner)
        digest = self._get_digest(index)
        self._add_digest(digest)
        self._inner[index] = value
        self._digest_value(index, value)

    def __delitem__(self, index):
        if index < 0:
            index += len(self._inner)
        for i in range(index, len(self) - 1):
            self[i] = self[i + 1]
        digest = self._get_digest(len(self) - 1)
        self._add_digest(digest)
        del self._inner[len(self) - 1]

    def insert(self, index, value):
        if index < 0:
            index += len(self._inner)
        buf = value
        for i in range(index, len(self)):
            v = self[i]
            self[i] = buf
            buf = v
        self.append(buf)

    def append(self, value):
        index = len(self)
        self._inner.append(value)
        self._digest_value(index, value)

    @property
    def digest(self):
        return self._digest

    def _get_digest(self, index):
        value = self._inner[index]
        if isinstance(value, Hashable):
            return self._digest_map[index][value]
        if isinstance(value, HashArray):
            return value.digest
        raise TypeError("Value must be hasharray or digestable")

    def _digest_value(self, index, value):
        if index not in self._digest_map:
            self._digest_map[index] = {}
        if isinstance(value, Hashable):
            if value not in self._digest_map[index]:
                self._digest_map[index][value] = random.randrange(1 << self._bit_size)
            self._add_digest(self._digest_map[index][value])
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self._add_digest, self._digest_map[index])
            self._inner[index] = value
        else:
            raise TypeError("Value must be mutable-sequence or digestable")

    def _add_digest(self, value: int):
        self._digest ^= value
        if self._callback is not None:
            self._callback(value)

    def __repr__(self):
        return self._inner.__repr__()


@dataclass
class State:
    __hash__ = None  # type: ignore
    _digest_map: ClassVar[dict] = {}
    _bit_size: ClassVar[int] = 60

    def __init_subclass__(cls) -> None:
        cls._digest_map = {}
        cls._bit_size = 60

    def __setattr__(self, name: str, value) -> None:
        if not name.startswith("_"):
            if hasattr(self, name):
                digest = self._get_digest(name)
                self._add_digest(digest)
            super().__setattr__(name, value)
            self._digest_value(name, value)
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if not name.startswith("_"):
            digest = self._get_digest(name)
            self._add_digest(digest)
        super().__delattr__(name)

    def _get_digest(self, name: str):
        value = getattr(self, name)
        if isinstance(value, Hashable):
            return self._digest_map[name][value]
        if isinstance(value, HashArray):
            return value.digest
        raise TypeError("Value must be hasharray or digestable")

    def _digest_value(self, name: str, value):
        if name not in self._digest_map:
            self._digest_map[name] = {}
        if isinstance(value, Hashable):
            if value not in self._digest_map[name]:
                self._digest_map[name][value] = random.randrange(1 << self._bit_size)
            self._add_digest(self._digest_map[name][value])
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self._add_digest, self._digest_map[name])
            super().__setattr__(name, value)
        else:
            raise TypeError("Value must be mutable-sequence or digestable")

    def _add_digest(self, value: int):
        if not hasattr(self, "_digest"):
            self._digest = 0
        self._digest ^= value

    @property
    def digest(self):
        return self._digest


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


@dataclass
class Solver:
    _game: Game = None  # type: ignore
    _hash_dict: dict[int, int] = field(default_factory=dict)
    _eval_list: array = field(default_factory=lambda: array("i"))
    _depth_list: array = field(default_factory=lambda: array("i"))
    _graph_inv: list[list[int]] = field(default_factory=list)
    _child_count_list: array = field(default_factory=lambda: array("I"))
    _queue_dict: dict[tuple[int, int], array] = field(default_factory=dict)
    _key_list: list[tuple[int, int]] = field(default_factory=list)

    @property
    def node_size(self):
        return len(self._eval_list)

    def solve(self, game: Game) -> Result:
        self._game = game
        start_sgg_time = time.time()
        init_idx = self._register_state(game.init_state)
        self._search_game_graph(game.init_state, init_idx)
        start_ra_time = time.time()
        self._retrograde_analyze()
        end_solve = time.time()
        sgg_time = start_ra_time - start_sgg_time
        ra_time = end_solve - start_ra_time
        return Result(
            hash_dict=self._hash_dict,
            eval_list=self._eval_list,
            depth_list=self._depth_list,
            sgg_time=sgg_time,
            ra_time=ra_time,
        )

    def _register_state(self, state: State) -> int:
        idx = self.node_size
        hash_dict = self._hash_dict
        for mirror_state in self._game.find_mirror_states(state):
            state_hash = mirror_state.digest
            if state_hash in hash_dict and hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            hash_dict[state_hash] = idx
        self._eval_list.append(0)
        self._depth_list.append(-1)
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _search_game_graph(self, state: State, idx: int) -> None:
        eval_list = self._eval_list
        depth_list = self._depth_list
        child_count_list = self._child_count_list
        graph_inv = self._graph_inv
        hash_dict = self._hash_dict
        evaluate_state = self._game.evaluate_state

        for next_state in self._game.find_next_states(state):
            next_hash = next_state.digest
            if next_hash in hash_dict:
                next_idx = hash_dict[next_hash]
            else:
                next_idx = self._register_state(next_state)
                next_res = evaluate_state(next_state)
                if next_res is not None:
                    eval_list[next_idx] = next_res
                    depth_list[next_idx] = 0
                else:
                    self._search_game_graph(next_state, next_idx)
            child_count_list[idx] += 1
            graph_inv[next_idx].append(idx)
        if child_count_list[idx] == 0:
            eval_list[idx] = self._game.default_eval
            depth_list[idx] = 0

    def _retrograde_analyze(self) -> None:  # noqa: C901
        child_count_list = self._child_count_list
        confirm_eval = self._confirm_eval
        for idx in range(self.node_size):
            if child_count_list[idx] == 0:
                confirm_eval(idx)
        while self._key_list:
            key = heappop(self._key_list)
            queue = self._queue_dict.pop(key)
            for idx in queue:
                confirm_eval(idx)
        for idx in range(self.node_size):
            if child_count_list[idx] > 0:
                self._eval_list[idx] = 0
                self._depth_list[idx] = -1

    def _confirm_eval(self, idx: int):  # noqa: C901
        eval_list = self._eval_list
        depth_list = self._depth_list
        child_count_list = self._child_count_list
        prev_ev, prev_depth = -eval_list[idx], depth_list[idx] + 1
        for prev_idx in self._graph_inv[idx]:
            if child_count_list[prev_idx] == 0:
                continue
            child_count_list[prev_idx] -= 1
            if self._is_better_eval(prev_ev, prev_depth, prev_idx):
                eval_list[prev_idx] = prev_ev
                depth_list[prev_idx] = prev_depth
                if prev_ev >= 0:
                    self._add_to_queue(prev_idx)
            if child_count_list[prev_idx] == 0:
                self._confirm_eval(prev_idx)
        child_count_list[idx] = 0
        self._graph_inv[idx].clear()

    def _is_better_eval(self, ev: int, depth: int, idx: int):
        if self._depth_list[idx] == -1:
            return True
        if self._eval_list[idx] < ev:
            return True
        return self._eval_list[idx] == ev and ev * depth < self._eval_list[idx] * self._depth_list[idx]

    def _add_to_queue(self, idx: int):
        ev, depth = self._eval_list[idx], self._depth_list[idx]
        key = (-ev, ev * depth)
        arr = self._queue_dict.get(key)
        if arr is None:
            arr = array("I")
            self._queue_dict[key] = arr
            heappush(self._key_list, key)
        arr.append(idx)


@dataclass
class Result:
    hash_dict: dict[int, int]
    eval_list: array
    depth_list: array
    sgg_time: float
    ra_time: float

    def state_to_params(self, state: State) -> tuple[int, int] | None:
        state_hash = state.digest
        if state_hash in self.hash_dict:
            idx = self.hash_dict[state_hash]
            return self.eval_list[idx], self.depth_list[idx]
        return None


@dataclass
class StonesState(State):
    stones: int


class Stones(Game):
    def __init__(self, init_stones, hand_list):
        self.init_state = StonesState(stones=init_stones)
        self.hand_list = hand_list
        self.default_eval = -1

    def find_next_states(self, state):
        stones = state.stones
        for hand in self.hand_list:
            next_stones = stones - hand
            if next_stones >= 0:
                state.stones = next_stones
                yield state
        state.stones = stones

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        return None


n, k = map(int, input().split())
a_list = list(map(int, input().split()))
stones = Stones(init_stones=k, hand_list=a_list)
solver = Solver()
result = solver.solve(stones)

ev, _ = result.state_to_params(stones.init_state)
if ev == 1:
    print("First")
else:
    print("Second")
