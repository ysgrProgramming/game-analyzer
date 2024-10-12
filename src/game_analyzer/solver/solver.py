from __future__ import annotations

import random
from dataclasses import dataclass

from game_analyzer import Game, Result, State
from game_analyzer.util import EvalParamsConverter

import numpy as np

@dataclass
class Solver:
    _game: Game | None = None
    _ep_conv: EvalParamsConverter | None = None
    _hash_dict: dict[int, int] = {}
    _eval_list: list[int | None] = []
    _graph_inv: list[list[int]] = []
    _child_count_list: list[int] = []

    def solve(self, game: Game, max_depth: int = 10000) -> Result:
        self._game = game
        self._ep_conv = EvalParamsConverter(max_depth)
        init_idx = self._register_state(game.init_state)
        self._search_state_eval(game.init_state, init_idx, max_depth)
        return Result(hash_dict=self._hash_dict, eval_list=self._eval_list)

    def _search_state_eval(self, state: State, idx: int, depth: int) -> int:
        min_eval = self._ep_conv.params_to_eval(-1, 0)
        eval_tmp = min_eval
        for next_state in self._game.find_next_states(state):
            next_hash = next_state.to_hash()
            if next_hash in self._hash_dict:
                next_idx = self._hash_dict[next_hash]
            else:
                next_idx = self._register_state(next_state)
                next_res = self._game.evaluate_state(next_state)
                if next_res is not None:
                    next_eval = self._ep_conv.params_to_eval(next_res, 0)
                    self._confirm_eval(next_idx, next_eval)
                else:
                    next_res = self._search_state_eval(next_state, next_idx, depth-1)
            if self._is_confirmed(next_idx):
                next_eval = self._eval_list[next_idx]
                eval_tmp = max(eval_tmp, self._ep_conv.next_eval(next_eval))
            else:
                self._child_count_list[idx] += 1
                self._graph_inv[next_idx].append(idx)

    def _register_state(self, state: State) -> int:
        idx = len(self._eval_list)
        min_hash = -1
        for mirror_state in self._game.find_mirror_states(state):
            state_hash = mirror_state.to_hash()
            if state_hash in self._hash_dict and self._hash_dict[state_hash] != idx:
                raise Exception("mirror func error")
            self._hash_dict[state_hash] = idx
            min_hash = min(min_hash, state_hash)

        self._graph_inv.append([])
        self._eval_list.append(None)
        self._child_count_list.append(0)
        return idx

    def _confirm_eval(self, idx: int, ev: int):
        self._eval_list[idx] = ev
        for prev_idx in self._graph_inv[idx]:
            self._eval_list[prev_idx] = max(self._eval_list[prev_idx], ev)
            self._child_count_list[prev_idx] -= 1
            if self._child_count_list[prev_idx] == 0:
                self._confirm_eval(prev_idx, ev)
        self._graph_inv[idx] = []

    def _is_confirmed(self, idx: int):
        ev = self._eval_list[idx]
        child_count = self._child_count_list[idx]
        return (ev is not None and child_count == 0)

    def classify_next_patterns(self, now_state: np.ndarray) -> dict[int, int]:
        next_hash_dict = {}
        for next_state in self._game.find_next_states(now_state):
            next_hash = self._game.state_to_hash(next_state)
            if next_hash not in self.hash_dict: continue
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
                    if eval <= min_eval: state_list.append(state)
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

    # def solve(self, game: Game, max_depth: int = 1000) -> Result:
    #     self.game = game
    #     self.ep_conv = EvalParamsConverter(max_depth)
    #     init_idx = self._register_state(game.init_state)
    #     extention_todo = [init_idx]
    #     min_eval = self.ep_conv.params_to_eval(-1, 0)
    #     while extention_todo:
    #         idx = extention_todo.pop()
    #         hash = self.hash_list[idx]
    #         state = self.sh_conv.hash_to_state(hash)
    #         eval_tmp = min_eval
    #         for next_state in game.find_next_states(state):
    #             next_hash = self.sh_conv.state_to_hash(next_state)
    #             if next_hash in self.hash_dict:
    #                 next_idx = self.hash_dict[next_hash]
    #             else:
    #                 next_idx = self._register_state(next_state)
    #                 next_res = game.evaluate_state(next_state)
    #                 if next_res is not None:
    #                     next_eval = self.ep_conv.params_to_eval(next_res, 0)
    #                     self.confirm_eval(next_idx, next_eval)
    #                 else: extention_todo.append(next_idx)
    #             if self._is_confirmed(next_idx):
    #                 next_eval = self._eval_list[next_idx]
    #                 eval_tmp = max(eval_tmp, self.ep_conv.next_eval(next_eval))
    #             else:
    #                 self._child_count_list[idx] += 1
    #                 self._graph_inv[next_idx].append(idx)
    #         if eval_tmp == min_eval:
    #             eval = self.game.default_eval
    #             self.confirm_eval(idx, eval)
    #         else:
    #             self._eval_list[idx] = eval
    #     draw_eval = self.ep_conv.params_to_eval(0, 0)
    #     for idx in range(len(self.hash_list)):
    #         self._graph_inv[idx] = []
    #         if self._child_count_list[idx] > 0:
    #             self._child_count_list[idx] = 0
    #             self._eval_list[idx] = max(self._eval_list[idx], draw_eval)

    #     result = Result(hash_list=self.hash_list, eval_list=self._eval_list)
    #     return result