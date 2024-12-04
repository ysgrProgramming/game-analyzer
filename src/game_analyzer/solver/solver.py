from __future__ import annotations

from dataclasses import dataclass, field

from game_analyzer import Game, Result, State
from game_analyzer.util import EvalParamsConverter

import sys

sys.setrecursionlimit(10**9)


@dataclass
class Solver:
    max_depth: int = 10000
    _game: Game = None  # type: ignore
    _ep_conv: EvalParamsConverter = None  # type: ignore
    _hash_dict: dict[int, int] = field(default_factory=dict)
    _eval_list: list[int] = field(default_factory=list)
    _graph_inv: list[list[int]] = field(default_factory=list)
    _child_count_list: list[int] = field(default_factory=list)
    _queue_list: list[list[int]] = field(default_factory=list)

    def __post_init__(self):
        self._ep_conv = EvalParamsConverter(max_depth=self.max_depth)

    @property
    def node_size(self):
        return len(self._eval_list)

    def solve(self, game: Game) -> Result:
        self._game = game
        init_idx = self._register_state(game.init_state)
        self._search_game_graph(game.init_state, init_idx)
        self._retrograde_analyze()
        return Result(hash_dict=self._hash_dict, eval_list=self._eval_list, max_depth=self.max_depth)

    def _search_game_graph(self, state: State, idx: int) -> None:
        for next_state in self._game.find_next_states(state):
            next_hash = next_state.to_hash()
            if next_hash in self._hash_dict:
                next_idx = self._hash_dict[next_hash]
            else:
                next_idx = self._register_state(next_state)
                next_res = self._game.evaluate_state(next_state)
                if next_res is not None:
                    self._eval_list[next_idx] = self._ep_conv.params_to_eval(next_res, 0)
                else:
                    self._search_game_graph(next_state, next_idx)
            self._child_count_list[idx] += 1
            self._graph_inv[next_idx].append(idx)
        if self._child_count_list[idx] == 0:
            self._eval_list[idx] = self._ep_conv.params_to_eval(self._game.default_eval, 0)

    def _retrograde_analyze(self):
        for idx in range(self.node_size):
            if self._child_count_list[idx] == 0:
                self._confirm_eval(idx)
        cursor = 0
        while cursor < len(self._queue_list):
            todo = self._queue_list[cursor]
            for idx in todo:
                self._confirm_eval(idx)
            self._queue_list[cursor] = []
            cursor += 1

    def _register_state(self, state: State) -> int:
        idx = len(self._eval_list)
        for mirror_state in self._game.find_mirror_states(state):
            state_hash: int = mirror_state.to_hash()  # type: ignore
            if state_hash in self._hash_dict and self._hash_dict[state_hash] != idx:
                msg = "mirror func error"
                raise ValueError(msg)
            self._hash_dict[state_hash] = idx
        self._eval_list.append(self._ep_conv.params_to_eval(-1, 0))
        self._graph_inv.append([])
        self._child_count_list.append(0)
        return idx

    def _confirm_eval(self, idx: int):
        ev = self._eval_list[idx]
        prev_ev = -self._ep_conv.prev_eval(ev)
        for prev_idx in self._graph_inv[idx]:
            if self._eval_list[prev_idx] < prev_ev:
                self._eval_list[prev_idx] = prev_ev
                self._child_count_list[prev_idx] -= 1
                if prev_ev > 0:
                    self._add_to_queue(prev_idx)
            self._child_count_list[prev_idx] -= 1
            if self._child_count_list[prev_idx] == 0:
                self._confirm_eval(prev_idx)
        self._graph_inv[idx] = []
        self._child_count_list[idx] = 0

    def _add_to_queue(self, idx: int):
        _, depth = self._ep_conv.eval_to_params(self._eval_list[idx])
        if len(self._queue_list) < depth+1:
            self._queue_list.extend([[] for _ in range(depth+1-len(self._queue_list))])
        self._queue_list[depth].append(idx)
