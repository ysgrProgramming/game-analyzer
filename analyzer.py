import numpy as np 
from collections import deque
import random
from typing import Tuple, List, Dict
import time

class Analyzer():
    def __init__(self, init_mat: np.ndarray[int], max_mat: np.ndarray[int], next_func, sym_func=lambda mat: [mat.copy()], end_func=lambda mat: None, default=0):
        self.dim = len(init_mat.shape)
        self.init_mat = init_mat
        self.max_mat = max_mat
        self.default = default
        if self.init_mat.shape != self.max_mat.shape:
            raise Exception("init_mat and max_mat shape mismatched")
        
        self.base1_mat, self.base2_mat = self._create_base_mat(max_mat)
        self.max_hash: int = np.max(self.base2_mat)

        self.next_func = next_func
        self.sym_func = sym_func
        self.end_func = end_func
        
        self.hash_list = []
        self.hash_dict = dict()
        self.eval_list = []
        self.step_list = []
        self.graph = []
        self.graph_inv = []
        self.child_count_list = []

    def _create_base_mat(self, max_mat: np.ndarray[int]) -> Tuple[np.ndarray, np.ndarray]:
        if np.count_nonzero(max_mat <= 0) > 0: raise Exception("max_mat must not contains 0 or negative")
        max_mat += 1
        s = max_mat.shape
        flat_mat = max_mat.ravel()
        ac_list = [1]
        for num in flat_mat:
            ac_list.append(int(num)*ac_list[-1])
        ac_mat = np.array(ac_list)
        base1_mat = ac_mat[:-1].reshape(s)
        base2_mat = ac_mat[1:].reshape(s)

        return base1_mat, base2_mat
    
    def hash_to_mat(self, hash: int) -> np.ndarray:
        mat = hash % self.base2_mat // self.base1_mat
        return mat

    def mat_to_min_hash(self, mat: np.ndarray) -> int:
        hash = self.max_hash
        for sym_mat in self.sym_func(mat):
            sym_hash = np.sum(sym_mat * self.base1_mat)
            if sym_hash < hash:
                hash = sym_hash
        return hash

    # eval(3:uc(skiped), 2:uc(cycle), 1:win, 0:draw, -1:lose, -2:uc(week))
    def merge(self, p_block, c_block, rel_depth):
        ev1, depth1 = p_block[1], p_block[2]
        ev2, depth2 = c_block[1], c_block[2]
        if ev2 == -2:
            ev2 = 2
            depth2 = 1
        elif ev2 <= 1:
            ev2 = -ev2
        depth2 += 1
        if ev2 == 1:
            p_block[3] = min(p_block[3], depth2+rel_depth)
        if ev2 == 2:
            c_ind = c_block[0]
            p_ind = p_block[0]
            self.graph_inv[c_ind].append(p_ind)
            self.child_count_list[p_ind] += 1
        if ev1 < ev2:
            ev1, ev2 = ev2, ev1
            depth1, depth2 = depth2, depth1
        if ev1 == ev2:
            if ev1 < 0:
                p_block[1] = ev1
                p_block[2] = max(depth1, depth2)
            else:
                p_block[1] = ev2
                p_block[2] = min(depth1, depth2)
        elif ev2 >= 1:
            if depth1 >= depth2:
                p_block[1] = ev2
                p_block[2] = depth2
        else:
            p_block[1] = ev1
            p_block[2] = depth1

    def add_hash(self, hash, ev=3, step=0):
        ind = len(self.hash_list)
        self.hash_list.append(hash)
        self.hash_dict[hash] = ind
        self.eval_list.append(ev)
        self.step_list.append(step)
        self.graph.append([])
        self.graph_inv.append([])
        self.child_count_list.append(0)
        return ind

    def register(self, block):
        ind, ev, step = block[0], block[1], block[2]
        self.eval_list[ind] = ev
        self.step_list[ind] = step

    def alpha_beta_analyze(self, max_step=10**15, rel_depth=0):
        
        print("\n--- start alpha beta analyze ---\n")

        start_time = time.time()
        print_time = start_time + 1
        init_hash = self.mat_to_min_hash(self.init_mat)
        self.add_hash(init_hash)

        #頂点番号、評価値、手数、深さ、次探索頂点リスト
        path = [[-1, -2, 0, max_step+1, [0]]]
        while True:
            block = path[-1]

            if time.time() >= print_time:
                t = print_time - start_time
                print(f"\r{t}s detected_states = {len(self.hash_list)}", end='')
                print_time += 1
            if len(block[4]) == 0:
                ind = block[0]
                if ind == -1: break
                path.pop()
                if block[1] == -2:
                    block[1] = self.default
                    block[2] = 0
                self.register(block)
                prev_block = path[-1]
                self.merge(prev_block, block, rel_depth)
            else:
                depth = block[3]-1
                next_ind = block[4].pop()
                if self.eval_list[next_ind] == 3 and self.step_list[next_ind] < depth:
                    next_block = [next_ind, -2, 0, depth, []]
                    path.append(next_block)
                    self.register(next_block)
                    next_hash = self.hash_list[next_ind]
                    next_mat = self.hash_to_mat(next_hash)
                    child_ind_set = set()
                    for child_mat in self.next_func(next_mat):
                        child_hash = self.mat_to_min_hash(child_mat)
                        if child_hash in self.hash_dict:
                            child_ind = self.hash_dict[child_hash]
                            if child_ind in child_ind_set: continue
                            child_ev = self.eval_list[child_ind]
                            child_step = self.step_list[child_ind]
                            if child_ev == 3 and child_step < depth-1:
                                next_block[4].append(child_ind)
                                child_ind_set.add(child_ind)
                            else:
                                child_block = [child_ind, child_ev, child_step, child_step, []]
                                self.merge(next_block, child_block, rel_depth)
                        else:
                            child_ind = self.add_hash(child_hash)
                            end_ev = self.end_func(child_mat)
                            if end_ev == None:
                                next_block[4].append(child_ind)
                                child_ind_set.add(child_ind)
                            else:
                                child_block = [child_ind, end_ev, 0, rel_depth, []]
                                self.register(child_block)
                                self.merge(next_block, child_block, rel_depth)
                elif self.eval_list[next_ind] == 3 and self.step_list[next_ind] == depth:
                    next_hash = self.hash_list[next_ind]
                    next_mat = self.hash_to_mat(next_hash)
                    for child_mat in self.next_func(next_mat):
                        next_block = [next_ind, self.eval_list[next_ind], self.step_list[next_ind], self.step_list[next_ind], []]
                        self.merge(block, next_block, rel_depth)
                        break
                    else:
                        next_block = [next_ind, -2, 0, 0, []]
                        path.append(next_block)
                else:
                    next_block = [next_ind, self.eval_list[next_ind], self.step_list[next_ind], self.step_list[next_ind], []]
                    self.merge(block, next_block, rel_depth)
        self.state_num = len(self.hash_list)

        print("\n-- alpha beta analyze finished --\n")

        print(f"total detected states = {self.state_num}")
        print(f"total elapsed time = {time.time()-start_time:.3f}")
        print("next, apply 'retrograde_analyze' to the states that could not be evaluated")
    
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
    
    def classify_next_patterns(self, now_mat: np.ndarray) -> Dict[Tuple[int, int], List[np.ndarray]]:
        next_mat_dict = dict()
        for next_mat in self.next_func(now_mat):
            next_hash = self.mat_to_min_hash(next_mat)
            next_ind = self.hash_dict[next_hash]
            step = self.step_list[next_ind]
            ev = self.eval_list[next_ind]
            if (step, ev) in next_mat_dict:
                next_mat_dict[(step, ev)].append(next_mat)
            else:
                next_mat_dict[(step, ev)] = [next_mat]
        return next_mat_dict
    
    def mat_to_status(self, mat: np.ndarray) -> Tuple[int, int]:
        hash = self.mat_to_min_hash(mat)
        ind = self.hash_dict[hash]
        step = self.step_list[ind]
        ev = self.eval_list[ind]
        return step, ev
    
    def list_example(self, mat: np.ndarray) -> List[np.ndarray]:
        if type(self.step_list) == None: raise Exception("make tree before list_example")

        log_list = [mat]
        while self.end_func(mat) == None:
            next_mat_dict = self.classify_next_patterns(mat)
            max_k = (0, 1)
            for k in next_mat_dict.keys():
                step, ev = k
                if max_k[1] > ev: max_k = k
                elif max_k[1] == ev:
                    if max_k[0]*max_k[1] < step*ev: max_k = k
                    elif max_k[0]*max_k[1] == step*ev:
                        if max_k[0] < step: max_k = k
            next_mat = random.choice(next_mat_dict[max_k])
            log_list.append(next_mat)
            mat = next_mat
        return log_list