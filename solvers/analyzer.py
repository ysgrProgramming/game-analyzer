import numpy as np 
from collections import deque
import random
from games import Game
from result import Result
from util import Converter
import time

class StrongSolver():
    def analyze(self):
        self.alpha_beta_analyze2(self.init_mat, self.max_search_depth)

    def solve(self, game: Game, max_depth: int = 1000) -> Result:
        hash_list: list[int] = []
        hash_dict: dict[int, int] = []
        eval_list: list[int | None] = []
        graph_inv: list[list[int]] = []
        child_count_list: list[int] = []

        converter = Converter(game.shape, game.range_of_elements)

    #todo: eval関連ずるしない
    #todo: 履歴追加
    def alpha_beta_analyze(self, mat: np.ndarray, max_depth: int, history: dict[int, int] = dict()) -> tuple[int, int]:
        hash = self.mat_to_hash(mat)

        if hash in self.hash_dict:
            idx = self.hash_dict[hash]
            if idx in history and history[idx] == len(history)-1:
                draw_eval = self.params_to_eval(0, 0)
                max_eval, min_eval = draw_eval, draw_eval
                return max_eval, min_eval
            max_eval = self.max_eval_list[idx]
            min_eval = self.min_eval_list[idx]
            if not (max_eval == self.params_to_eval(1, 1) and min_eval == self.params_to_eval(-1, 1) and idx not in history and max_depth > 0):
                return max_eval, min_eval
            end_eval = None
        else:
            idx = self.add_mat(mat)
            end_eval = self.end_func(mat)
        
        history_idx = len(history)
        history[idx] = history_idx
        if end_eval is None:
            max_eval, max_prop_eval, min_eval = self.params_to_eval(1, 1), self.params_to_eval(-1, 1), self.params_to_eval(-1, 1)
            is_next_empty = True
            self.max_eval_list[idx] = max_eval
            self.min_eval_list[idx] = min_eval
            for next_mat in self.next_func(mat):
                if max_depth <= 0: break
                is_next_empty = False
                next_max_eval, next_min_eval = self.alpha_beta_analyze(next_mat, max_depth-1)
                maybe_max_eval = -self.next_eval(next_min_eval)
                maybe_min_eval = -self.next_eval(next_max_eval)
                max_prop_eval = max(max_prop_eval, maybe_max_eval)
                min_eval = max(min_eval, maybe_min_eval)
                res, depth = self.eval_to_params(min_eval)
                if res == 1: max_depth = min(max_depth, depth + self.rel_search_depth)
            else:
                max_eval = max_prop_eval
            if is_next_empty:
                max_eval, min_eval = self.params_to_eval(self.default, 0), self.params_to_eval(self.default, 0)
        else:
            max_eval, min_eval = self.params_to_eval(end_eval, 0), self.params_to_eval(end_eval, 0)
        self.max_eval_list[idx] = max_eval
        self.min_eval_list[idx] = min_eval
        del history[idx]
        #print("max_eval =", self.eval_to_params(max_eval), "min_eval =", self.eval_to_params(min_eval), "end_eval =", end_eval, "max_depth =", max_depth)
        #print("idx =", idx)
        #print(mat)
        #print()
        return max_eval, min_eval
    
    def add_mat(self, mat: np.ndarray) -> int:
        idx = len(self.hash_list)
        min_hash = self.max_hash
        for hash in self.mat_to_all_hash(mat):
            if hash in self.hash_dict and self.hash_dict[hash] != idx: raise Exception("sym_func error")
            self.hash_dict[hash] = idx
            min_hash = min(min_hash, hash)
        self.hash_list.append(min_hash)

        self.graph.append([])
        self.graph_inv.append([])
        self.max_eval_list.append(self.params_to_eval(1, 0))
        self.min_eval_list.append(self.params_to_eval(-1, 0))
        self.child_count_list.append(0)
        return idx
    
    def retrograde_analyze(self):

        print("\n--- start retrograde analyze ---\n")
        
        start_time = time.time()
        print_time = start_time + 1
        done_states = self.state_num - sum(1 for i in range(self.state_num) if self.eval_list[i] == 2)
        todo = deque([i for i in range(self.state_num) if self.eval_list[i] == 2 and self.child_count_list[i] == 0])
        while todo:
            if time.time() >= print_time:
                t = print_time - start_time
                rate = done_states/self.state_num
                print(f"\r{t}s evaluated states = [{done_states}/{self.state_num}]({rate:.3f})", end='')
                print_time += 1

            ind = todo.popleft()
            block = [ind, -2, 0, 0, []]
            for next_ind in self.graph[ind]:
                next_block = [next_ind, self.eval_list[next_ind], self.step_list[next_ind], 0, []]
                self.merge(block, next_block)
            self.register(block)
            for prev_ind in self.graph_inv[ind]:
                self.child_count_list[prev_ind] -= 1
                if self.child_count_list[prev_ind] == 0:
                    todo.append(prev_ind)
        
        for i in range(self.state_num):
            if self.eval_list[i] == 2:
                self.eval_list[i] = 0
                self.step_list[i] = 0
            elif self.eval_list[i] == 3:
                self.eval_list[i] = -2
                self.step_list[i] = 0
            elif self.eval_list[i] == 0:
                self.step_list[i] = 0

        print("\n-- retrograde analyze finished --\n")

        print(f"total elapsed time = {time.time()-start_time:.3f}")
        print("analyze finished, You can use 'mat_to_status' or 'list_example' etc. to get the results of analysis.")
    
    def classify_next_patterns(self, now_mat: np.ndarray) -> dict[int, int]:
        next_hash_dict = dict()
        for next_mat in self.next_func(now_mat):
            next_hash = self.mat_to_hash(next_mat)
            if next_hash not in self.hash_dict: continue
            next_idx = self.hash_dict[next_hash]
            eval = self.min_eval_list[next_idx]
            if eval in next_hash_dict:
                next_hash_dict[next_hash].append(eval)
            else:
                next_hash_dict[next_hash] = eval
        return next_hash_dict
    
    def list_example(self, mat: np.ndarray) -> list[np.ndarray]:
        log_list = [mat]
        end_evalal = self.end_func(mat)
        if end_evalal is None:
            next_hash_dict = self.classify_next_patterns(mat)
            if len(next_hash_dict) > 0:
                min_eval = self.max_search_depth
                mat_list = []
                for hash, eval in next_hash_dict.items():
                    mat = self.hash_to_mat(hash)
                    if eval < min_eval:
                        mat_list = []
                        min_eval = eval
                    if eval <= min_eval: mat_list.append(mat)
                next_mat = random.choice(mat_list)
                log_list.extend(self.list_example(next_mat))
        return log_list

    def print_example(self, mat: np.ndarray):
        log_list = self.list_example(mat)
        for mat in log_list:
            hash = self.mat_to_hash(mat)
            idx = self.hash_dict[hash]
            max_eval = self.max_eval_list[idx]
            min_eval = self.min_eval_list[idx]
            max_res, max_depth = self.eval_to_params(max_eval)
            min_res, min_depth = self.eval_to_params(min_eval)
            print(f"max: res = {max_res}, depth = {max_depth}")
            print(f"min: res = {min_res}, depth = {min_depth}")
            print(mat, "\n")