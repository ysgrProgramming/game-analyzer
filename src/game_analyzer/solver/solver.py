from __future__ import annotations

import sys
import time
from array import array
from dataclasses import dataclass, field
from heapq import heappop, heappush

from game_analyzer import Game, HashState, Result, State

sys.setrecursionlimit(10**9)


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
        if isinstance(game.init_state, HashState):
            init_idx = self._register_state(game.init_state)
            self._search_game_graph_recursive(game.init_state, init_idx)
        else:
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
            state_hash: int = mirror_state.digest  # type: ignore
            if state_hash in hash_dict and hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            hash_dict[state_hash] = idx
        self._eval_list.append(0)
        self._depth_list.append(-1)
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _search_game_graph_recursive(self, state: State, idx: int) -> None:
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
                    self._search_game_graph_recursive(next_state, next_idx)
            child_count_list[idx] += 1
            graph_inv[next_idx].append(idx)
        if child_count_list[idx] == 0:
            eval_list[idx] = self._game.default_eval
            depth_list[idx] = 0

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
                next_hash = next_state.digest
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
            self._graph_inv[idx] = []

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
