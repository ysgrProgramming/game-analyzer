from __future__ import annotations

import random
from dataclasses import dataclass, field

from game_analyzer import Game, Result, State
from game_analyzer.util import EvalParamsConverter

import numpy as np

import sys

sys.setrecursionlimit(10**9)


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


class A:
    def classify_next_patterns(self, now_state: np.ndarray) -> dict[int, int]:
        next_hash_dict = {}
        for next_state in self._game.find_next_states(now_state):
            next_hash = self._game.state_to_hash(next_state)
            if next_hash not in self.hash_dict:
                continue
            next_idx = self.hash_dict[next_hash]
            eval = self.min_eval_list[next_idx]
            if eval in next_hash_dict:
                next_hash_dict[next_hash].append(eval)
            else:
                next_hash_dict[next_hash] = eval
        return next_hash_dict

    def list_example(self, state: np.ndarray) -> list[np.ndarray]:
        log_list = [state]
        end_evalal = self.end_func(state)
        if end_evalal is None:
            next_hash_dict = self.classify_next_patterns(state)
            if len(next_hash_dict) > 0:
                min_eval = self.max_search_depth
                state_list = []
                for hash, eval in next_hash_dict.items():
                    state = self.hash_to_state(hash)
                    if eval < min_eval:
                        state_list = []
                        min_eval = eval
                    if eval <= min_eval:
                        state_list.append(state)
                next_state = random.choice(state_list)
                log_list.extend(self.list_example(next_state))
        return log_list

    def print_example(self, state: np.ndarray):
        log_list = self.list_example(state)
        for state in log_list:
            hash = self.state_to_hash(state)
            idx = self.hash_dict[hash]
            max_eval = self.max_eval_list[idx]
            min_eval = self.min_eval_list[idx]
            max_res, max_depth = self.eval_to_params(max_eval)
            min_res, min_depth = self.eval_to_params(min_eval)
            print(f"max: res = {max_res}, depth = {max_depth}")
            print(f"min: res = {min_res}, depth = {min_depth}")
            print(state, "\n")
