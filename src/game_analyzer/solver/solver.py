from __future__ import annotations

from dataclasses import dataclass, field

from game_analyzer import Game, Result, State

from heapq import heappush, heappop
from array import array
import time
import sys

sys.setrecursionlimit(10**5)


def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


@dataclass
class Solver:
    _game: Game = None  # type: ignore
    _hash_dict: dict[int, int] = field(default_factory=dict)
    _eval_list: array = field(default_factory=lambda: array("i"))
    _depth_list: array = field(default_factory=lambda: array("i"))
    _graph_inv: list[list[int]] = field(default_factory=list)
    _child_count_list: array = field(default_factory=lambda: array("I"))
    _queue_dict: dict[tuple[int, int], list[int]] = field(default_factory=dict)
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

    def _search_game_graph(self, state: State, idx: int) -> None:
        for next_state in self._game.find_next_states(state):
            next_hash = next_state.to_hash()
            if next_hash in self._hash_dict:
                next_idx = self._hash_dict[next_hash]
            else:
                next_idx = self._register_state(next_state)
                next_res = self._game.evaluate_state(next_state)
                if next_res is not None:
                    self._eval_list[next_idx] = next_res
                    self._depth_list[idx] = 0
                else:
                    self._search_game_graph(next_state, next_idx)
            self._child_count_list[idx] += 1
            self._graph_inv[next_idx].append(idx)
        if self._child_count_list[idx] == 0:
            self._eval_list[idx] = self._game.default_eval
            self._depth_list[idx] = 0

    def _retrograde_analyze(self) -> None:  # noqa: C901
        for idx in range(self.node_size):
            if self._child_count_list[idx] == 0:
                self._confirm_eval(idx)
        while self._key_list:
            key = heappop(self._key_list)
            for idx in self._queue_dict[key]:
                self._confirm_eval(idx)
        for idx in range(self.node_size):
            if self._child_count_list[idx] > 0:
                self._eval_list[idx] = 0
                self._depth_list[idx] = -1

    def _register_state(self, state: State) -> int:
        idx = self.node_size
        for mirror_state in self._game.find_mirror_states(state):
            state_hash: int = mirror_state.to_hash()  # type: ignore
            if state_hash in self._hash_dict and self._hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            self._hash_dict[state_hash] = idx
        self._eval_list.append(0)
        self._depth_list.append(-1)
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _confirm_eval(self, idx: int):  # noqa: C901
        prev_ev, prev_depth = -self._eval_list[idx], self._depth_list[idx] + 1
        for prev_idx in self._graph_inv[idx]:
            if self._child_count_list[prev_idx] == 0:
                continue
            self._child_count_list[prev_idx] -= 1
            if self._is_eval_bigger(prev_ev, prev_depth, prev_idx):
                self._eval_list[prev_idx] = prev_ev
                self._depth_list[prev_idx] = prev_depth
                if prev_ev >= 0:
                    self._add_to_queue(prev_idx)
            if self._child_count_list[prev_idx] == 0:
                self._confirm_eval(prev_idx)
        self._graph_inv[idx].clear()

    def _is_eval_bigger(self, ev: int, depth: int, idx: int):
        if self._depth_list[idx] == -1:
            return True
        if self._eval_list[idx] < ev:
            return True
        return self._eval_list[idx] == ev and ev * depth < self._eval_list[idx] * self._depth_list[idx]

    def _add_to_queue(self, idx: int):
        ev, depth = self._eval_list[idx], self._depth_list[idx]
        key = (-ev, ev * depth)
        if key in self._queue_dict:
            self._queue_dict[key].append(idx)
        else:
            self._queue_dict[key] = [idx]
            heappush(self._key_list, key)
