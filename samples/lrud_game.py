from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from array import array
from collections.abc import Hashable, Iterable, MutableSequence
from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import ClassVar, Literal


@dataclass
class State:
    __hash__ = None
    _digest_map: ClassVar[dict] = {}
    _bit_size: ClassVar[int] = 60

    def __init_subclass__(cls) -> None:
        cls._digest_map = {}
        cls._bit_size = 60

    @property
    def digest(self) -> int:
        h = 0
        for k, v in self.to_dict().items():
            if k not in self._digest_map:
                self._digest_map[k] = {}
            h ^= self._get_obj_digest(v, self._digest_map[k])
        return h

    def to_dict(self) -> dict:
        return self.__dict__

    def _get_obj_digest(self, obj, mapping) -> int:
        if isinstance(obj, Hashable):
            if obj not in mapping:
                mapping[obj] = random.randrange(1 << self._bit_size)
            return mapping[obj]
        if isinstance(obj, MutableSequence):
            h = 0
            for i, v in enumerate(obj):
                if i not in mapping:
                    mapping[i] = {}
                h ^= self._get_obj_digest(v, mapping[i])
            return h
        raise TypeError("Value must be mutable-sequence or digestable")


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
        self._search_game_graph()
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
            state_hash: int = mirror_state.to_hash()  # type: ignore
            if state_hash in hash_dict and hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            hash_dict[state_hash] = idx
        self._eval_list.append(0)
        self._depth_list.append(-1)
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _search_game_graph(self) -> None:  # noqa: C901, PLR0914
        eval_list = self._eval_list
        depth_list = self._depth_list
        child_count_list = self._child_count_list
        graph_inv = self._graph_inv
        hash_dict = self._hash_dict
        evaluate_state = self._game.evaluate_state
        find_next_states = self._game.find_next_states
        register_state = self._register_state
        init_state = self._game.init_state

        todo = [init_state]
        todo_idx = array("I", [register_state(init_state)])
        while todo:
            state, idx = todo.pop(), todo_idx.pop()
            for next_state in find_next_states(state):
                next_hash = next_state.to_hash()
                next_idx = hash_dict.get(next_hash)
                if next_idx is None:
                    next_idx = register_state(next_state)
                    next_res = evaluate_state(next_state)
                    if next_res is None:
                        todo.append(next_state)
                        todo_idx.append(next_idx)
                    else:
                        eval_list[next_idx] = next_res
                        depth_list[next_idx] = 0
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

    def _confirm_eval(self, start_idx: int):  # noqa: C901
        eval_list = self._eval_list
        depth_list = self._depth_list
        child_count_list = self._child_count_list

        todo_idx = [start_idx]
        while todo_idx:
            idx = todo_idx.pop()
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
                    todo_idx.append(prev_idx)
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
        state_hash = state.to_hash()
        if state_hash in self.hash_dict:
            idx = self.hash_dict[state_hash]
            return self.eval_list[idx], self.depth_list[idx]
        return None


@dataclass
class LRUDState(State):
    r: int
    c: int
    step: int
    turn: Literal[0, 1]


class LRUD(Game):
    move_dict = {"L": (0, -1), "R": (0, 1), "U": (-1, 0), "D": (1, 0)}

    def __init__(self, h, w, init_cd, s_list, t_list, max_step):  # noqa: PLR0913, PLR0917
        self.h = h
        self.w = w
        self.s_list = s_list
        self.t_list = t_list
        self.max_step = max_step
        r, c = init_cd

        self.init_state = LRUDState(r=r, c=c, step=0, turn=0)

    def find_next_states(self, state):
        r, c, step, turn = state.r, state.c, state.step, state.turn
        if turn == 0:
            d = [(0, 0), self.move_dict[self.s_list[step]]]
            for dr, dc in d:
                yield LRUDState(r=r + dr, c=c + dc, step=step, turn=1)
        else:
            d = [(0, 0), self.move_dict[self.t_list[step]]]
            for dr, dc in d:
                yield LRUDState(r=r + dr, c=c + dc, step=step + 1, turn=0)

    @staticmethod
    def find_mirror_states(state):
        yield state

    def evaluate_state(self, state):
        r, c, step, turn = state.r, state.c, state.step, state.turn
        if not self._is_on_board(r, c):
            if turn == 0:
                return 1
            return -1
        if step == self.max_step:
            if turn == 0:
                return -1
            return 1
        return None

    def _is_on_board(self, r, c):
        return 1 <= r <= self.h and 1 <= c <= self.w


if __name__ == "__main__":
    h, w, n = map(int, input().split())
    sr, sc = map(int, input().split())
    s = input()
    t = input()
    lrud = LRUD(h=h, w=w, init_cd=(sr, sc), s_list=s, t_list=t, max_step=n)
    solver = Solver()
    result = solver.solve(lrud)
    ev, _ = result.state_to_params(lrud.init_state)

    if ev == 1:
        print("NO")
    else:
        print("YES")
