import numpy as np
import random
from game import Game
from result import Result
from util import StateHashConverter, EvalParamsConverter
from .base import Solver
from dataclasses import dataclass

@dataclass
class StrongSolver(Solver):
    hash_list: list[int] = []
    hash_dict: dict[int, int] = dict()
    eval_list: list[int | None] = []
    graph_inv: list[list[int]] = []
    child_count_list: list[int] = []
    game: Game
    sh_conv: StateHashConverter
    ep_conv: EvalParamsConverter

    def solve(self, game: Game, max_depth: int = 1000) -> Result:
        self.game = game
        self.sh_conv = StateHashConverter(shape=game.shape, range_of_elements=game.range_of_elements)
        self.ep_conv = EvalParamsConverter(max_depth=max_depth)

        init_idx = self.register_state(game.init_state)
        extention_todo = [init_idx]
        min_eval = self.ep_conv.params_to_eval(-1, 0)
        while extention_todo:
            idx = extention_todo.pop()
            hash = self.hash_list[idx]
            state = self.sh_conv.hash_to_state(hash)
            eval_tmp = min_eval
            for next_state in game.find_next_states(state):
                next_hash = self.sh_conv.state_to_hash(next_state)
                if next_hash in self.hash_dict:
                    next_idx = self.hash_dict[next_hash]
                else:
                    next_idx = self.register_state(next_state)
                    next_res = game.evaluate_state(next_state)
                    if next_res is not None:
                        next_eval = self.ep_conv.params_to_eval(next_res, 0)
                        self.confirm(next_idx, next_eval)
                    else: extention_todo.append(next_idx)
                if self.is_confirmed(next_idx):
                    next_eval = self.eval_list[next_idx]
                    eval_tmp = max(eval_tmp, self.ep_conv.next_eval(next_eval))
                else:
                    self.child_count_list[idx] += 1
                    self.graph_inv[next_idx].append(idx)
            if eval_tmp == min_eval:
                eval = self.game.default_eval
                self.confirm(idx, eval)
            else:
                self.eval_list[idx] = eval
        draw_eval = self.ep_conv.params_to_eval(0, 0)
        for idx in range(len(self.hash_list)):
            self.graph_inv[idx] = []
            if self.child_count_list[idx] > 0:
                self.child_count_list[idx] = 0
                self.eval_list[idx] = max(self.eval_list[idx], draw_eval)

        result = Result(hash_list=self.hash_list, eval_list=self.eval_list)
        return result
    
    def register_state(self, state: np.ndarray) -> int:
        idx = len(self.hash_list)
        min_hash = self.sh_conv.max_hash
        for mirror_state in self.game.find_mirror_states(state):
            hash = self.sh_conv.state_to_hash(mirror_state)
            if hash in self.hash_dict and self.hash_dict[hash] != idx: raise Exception("mirror func error")
            self.hash_dict[hash] = idx
            min_hash = min(min_hash, hash)
        self.hash_list.append(min_hash)
        
        self.graph_inv.append([])
        self.eval_list.append(None)
        self.child_count_list.append(0)
        return idx
    
    def confirm(self, init_idx: int, init_eval: int):
        todo = [init_idx]
        self.eval_list[init_idx] = init_eval
        while todo:
            idx = todo.pop()
            eval = self.ep_conv.next_eval(self.eval_list[idx])
            for prev_idx in self.graph_inv[idx]:
                self.eval_list[prev_idx] = max(self.eval_list[prev_idx], eval)
                self.child_count_list[prev_idx] -= 1
                if self.child_count_list[prev_idx] == 0:
                    todo.append(prev_idx)
            self.graph_inv[idx] = []

    def is_confirmed(self, idx: int):
        eval = self.eval_list[idx]
        child_count = self.child_count_list[idx]
        return (eval is not None and child_count == 0)
    
    def classify_next_patterns(self, now_state: np.ndarray) -> dict[int, int]:
        next_hash_dict = dict()
        for next_state in self.next_func(now_state):
            next_hash = self.state_to_hash(next_state)
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