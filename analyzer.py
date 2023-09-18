import numpy as np 
from collections import deque
import random
from typing import Tuple, List, Dict

class Analyzer():
    def __init__(self, init_mat: np.ndarray[int], max_mat: np.ndarray[int], next_func, sym_func=lambda mat: mat.copy(), end_func=lambda mat: None, default=0):
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
        
        self.hash_list = [-1]
        self.hash_dict = dict()
        self.eval_list = [3]
        self.depth_list = [0]
        self.graph_inv = [[]]
        self.child_count_list = [0]

    def _create_base_mat(self, max_mat: np.ndarray[int]) -> Tuple[np.ndarray, np.ndarray]:
        if np.count_nonzero(max_mat <= 0) > 0: raise Exception("max_mat must not contains 0 or negative")
        s = max_mat.shape
        flat_mat = max_mat.ravel()
        ac_list = [1]
        for num in flat_mat:
            ac_list.append(num*ac_list[-1])
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
            hash = min(hash, np.sum(sym_mat * self.base1_mat))
            if hash in self.hash_dict: return hash
        return hash

    # eval(3:uc(skiped), 2:uc(cycle), 1:win, 0:draw, -1:lose, -2:uc(week), )
    def merge(self, p_ind, c_ind):
        ev1, depth1 = self.eval_list[p_ind], self.depth_list[p_ind]
        ev2, depth2 = self.eval_list[c_ind], self.depth_list[c_ind]
        if ev2 == -2:
            ev2 = 2
            depth2 = 0
        elif ev2 <= 1:
            ev2 = -ev2
        depth2 += 1
        if ev2 == 2:
            self.graph_inv[c_ind].append(p_ind)
            self.child_count_list[p_ind] += 1
        if ev1 < ev2:
            ev1, ev2 = ev2, ev1
            depth1, depth2 = depth2, depth1
        if ev1 == ev2:
            if ev1 < 0:
                self.eval_list[p_ind] = ev1
                self.depth_list[p_ind] = max(depth1, depth2)
            else:
                self.eval_list[p_ind] = ev2
                self.depth_list[p_ind] = min(depth1, depth2)
        elif ev2 >= 1:
            if depth1 >= depth2:
                self.eval_list[p_ind] = ev2
                self.depth_list[p_ind] = depth2
        else:
            self.eval_list[p_ind] = ev1
            self.depth_list[p_ind] = depth1
    
    def add_hash(self, hash, ev=3, depth=-float('inf')):
        ind = len(self.hash_list)
        self.hash_list.append(hash)
        self.hash_dict[hash] = ind
        self.eval_list.append(ev)
        self.depth_list.append(depth)
        self.graph_inv.append([])
        self.child_count_list.append(0)
        return ind

    def week_solve(self, max_depth=float('inf'), rel_depth=0):
        init_hash = self.mat_to_min_hash(self.init_mat)

        todo = [self.add_hash(init_hash)]
        path = [[0, max_depth]]
        while todo:
            ind = todo[-1]
            path_ind, path_left = path[-1]

            print(self.hash_to_mat(self.hash_list[ind]))
            print(path)
            print(self.eval_list[ind], self.depth_list[ind])

            if path_ind == ind:
                #帰りがけ
                path.pop()
                todo.pop()
                p_ind, p_left = path[-1]
                if self.eval_list[path_ind] > 0:
                    path[-1][1] = min(p_left, path_left+1)
                self.merge(p_ind, path_ind)
            else:
                #行きがけ
                left = path_left-1
                if left <= 0:
                    self.eval_list[ind] = 3
                    self.depth_list[ind] = left
                    todo.pop()
                    self.merge(path_ind, ind)
                    continue
                if self.eval_list[ind] == 3 and self.depth_list[ind] < left:
                    self.eval_list[ind] = -2
                    self.depth_list[ind] = 0
                elif self.eval_list[ind] != -2:
                    todo.pop()
                    self.merge(path_ind, ind)
                    continue

                path.append([ind, left])
                hash = self.hash_list[ind]
                mat = self.hash_to_mat(hash)

                next_ind_set = set()
                for next_mat in self.next_func(mat):
                    next_hash = self.mat_to_min_hash(next_mat)
                    if next_hash in self.hash_dict:
                        next_ind = self.hash_dict[next_hash]
                        if next_ind in next_ind_set: continue
                        if self.eval_list[next_ind] == 3 and self.depth_list[next_ind] < left-1:
                            self.eval_list[next_ind] = -2
                            self.depth_list[next_ind] = 0
                            next_ind_set.add(next_ind)
                            todo.append(next_ind)
                        elif self.eval_list[next_ind] > 0:
                            left = self.depth_list[next_ind]
                            path[-1][1] = min(path_left, left+1)
                            self.merge(ind, next_ind)
                        else:
                            self.merge(ind, next_ind)
                    else:
                        next_ind = self.add_hash(next_hash)
                        end_ev = self.end_func(next_mat)
                        if end_ev != None:
                            self.depth_list[next_ind] = 0
                            self.eval_list[next_ind] = end_ev
                            left = rel_depth
                            path[-1][1] = min(path_left, left+1)
                            self.merge(ind, next_ind)
                        else:
                            next_ind_set.add(next_ind)
                            todo.append(next_ind)
                if len(next_ind_set) == 0:
                    self.eval_list[ind] = self.default
                    self.depth_list[ind] = 0
                    if self.default == 1:
                        path[-1][1] = rel_depth
        self.state_num = len(self.hash_list)
        print(self.eval_list)
        print(self.depth_list)

    def week_solve2(self, max_depth=float('inf'), rel_depth=0):
        init_hash = self.mat_to_min_hash(self.init_mat)

        todo = [self.add_hash(init_hash)]
        path = [[0, max_depth]]
        while todo:
            ind = todo[-1]
            path_ind, path_left = path[-1]

            print(self.hash_to_mat(self.hash_list[ind]))
            print(path)
            print(self.eval_list[ind], self.depth_list[ind])

            if path_ind == ind:
                #帰りがけ
                path.pop()
                todo.pop()
                p_ind, p_left = path[-1]
                if self.eval_list[path_ind] > 0:
                    path[-1][1] = min(p_left, path_left+1)
                self.merge(p_ind, path_ind)
            else:
                #行きがけ
                left = path_left-1
                if left <= 0:
                    self.eval_list[ind] = 3
                    self.depth_list[ind] = left
                    todo.pop()
                    self.merge(path_ind, ind)
                    continue
                if self.eval_list[ind] == 3 and self.depth_list[ind] < left:
                    self.eval_list[ind] = -2
                    self.depth_list[ind] = 0
                elif self.eval_list[ind] != -2:
                    todo.pop()
                    self.merge(path_ind, ind)
                    continue

                path.append([ind, left])
                hash = self.hash_list[ind]
                mat = self.hash_to_mat(hash)

                next_ind_set = set()
                for next_mat in self.next_func(mat):
                    next_hash = self.mat_to_min_hash(next_mat)
                    if next_hash in self.hash_dict:
                        next_ind = self.hash_dict[next_hash]
                        
                        if next_ind in next_ind_set: continue
                        if self.eval_list[next_ind] == 3 and self.depth_list[next_ind] < left-1:
                            self.eval_list[next_ind] = -2
                            self.depth_list[next_ind] = 0
                            next_ind_set.add(next_ind)
                            todo.append(next_ind)
                        elif self.eval_list[next_ind] > 0:
                            left = self.depth_list[next_ind]
                            path[-1][1] = min(path_left, left+1)
                            self.merge(ind, next_ind)
                        else:
                            self.merge(ind, next_ind)
                    else:
                        next_ind = self.add_hash(next_hash)
                        end_ev = self.end_func(next_mat)
                        if end_ev != None:
                            self.depth_list[next_ind] = 0
                            self.eval_list[next_ind] = end_ev
                            left = rel_depth
                            path[-1][1] = min(path_left, left+1)
                            self.merge(ind, next_ind)
                        else:
                            next_ind_set.add(next_ind)
                            todo.append(next_ind)
                if len(next_ind_set) == 0:
                    self.eval_list[ind] = self.default
                    self.depth_list[ind] = 0
                    if self.default == 1:
                        path[-1][1] = rel_depth
        self.state_num = len(self.hash_list)
        print(self.eval_list)
        print(self.depth_list)
    
    def construct_game_graph(self):
        init_hash = self._mat_to_hash(self.init_mat)
        self.graph = [[]]
        self.graph_inv = [[]]
        self.hash_list = [init_hash]
        self.hash_dict = {init_hash: 0}
        todo = [0]
        while todo:
            ind = todo.pop()
            hash = self.hash_list[ind]
            mat = self.hash_to_mat(hash)

            if self.end_func(mat) != None: continue
            for next_mat in self.next_func(mat):
                next_hash = self.mat_to_min_hash(next_mat)
                if next_hash in self.hash_dict:
                    next_ind = self.hash_dict[next_hash]
                    self.graph[ind].append(next_ind)
                    self.graph_inv[next_ind].append(ind)
                else:
                    next_ind = len(self.hash_list)
                    self.hash_list.append(next_hash)
                    self.hash_dict[next_hash] = next_ind
                    self.graph.append([])
                    self.graph_inv.append([])
                    self.graph[ind].append(next_ind)
                    self.graph_inv[next_ind].append(ind)
                    todo.append(next_ind)
        
        self.state_num = len(self.hash_list)
    
    def solve_game_graph(self):
        if type(self.graph) == None: raise Exception("construct game graph before make tree")

        self.dist_mat = np.full(self.state_num, -1, np.int32)
        self.judge_mat = np.full(self.state_num, -1, np.int8)
        child_count_mat = np.empty(self.state_num, np.int32)

        todo = deque([])
        for i in range(self.state_num):
            child_count_mat[i] = len(self.graph[i])
            if child_count_mat[i] == 0:
                self.dist_mat[i] = 0
                todo.append(i)

                hash = self.hash_list[i]
                mat = self.hash_to_mat(hash)
                self.judge_mat[i] = self.end_func(mat)+1
        
        while todo:
            ind = todo.popleft()
            dist = self.dist_mat[ind]
            judge = self.judge_mat[ind]
            if judge != 0:
                for node in self.graph_inv[ind]:
                    if self.dist_mat[node] != -1: continue
                    child_count_mat[node] -= 1
                    self.judge_mat[node] = max(self.judge_mat[node], -judge+2)
                    if child_count_mat[node] == 0:
                        self.dist_mat[node] = dist + 1
                        todo.append(node)
            else:
                for node in self.graph_inv[ind]:
                    if self.dist_mat[node] != -1: continue
                    self.judge_mat[node] = 2
                    self.dist_mat[node] = dist + 1
                    todo.append(node)
        
        self.judge_mat[self.judge_mat == -1] = 1
        self.judge_mat -= 1
    
    def classify_next_patterns(self, now_mat: np.ndarray) -> Dict[Tuple[int, int], List[np.ndarray]]:
        next_mat_dict = dict()
        for next_mat in self.next_func(now_mat):
            next_hash = self.mat_to_min_hash(next_mat)
            next_ind = self.hash_dict[next_hash]
            dist = self.dist_mat[next_ind]
            judge = self.judge_mat[next_ind]
            if (dist, judge) in next_mat_dict:
                next_mat_dict[(dist, judge)].append(next_mat)
            else:
                next_mat_dict[(dist, judge)] = [next_mat]
        return next_mat_dict
    
    def mat_to_status(self, mat: np.ndarray) -> Tuple[int, int]:
        hash = self.mat_to_min_hash(mat)
        ind = self.hash_dict[hash]
        dist = self.dist_mat[ind]
        judge = self.judge_mat[ind]
        return dist, judge
    
    def list_example(self, mat: np.ndarray) -> List[np.ndarray]:
        if type(self.dist_mat) == None: raise Exception("make tree before list_example")

        log_list = [mat]
        while self.end_func(mat) == None:
            next_mat_dict = self.classify_next_patterns(mat)
            max_k = (0, 1)
            for k in next_mat_dict.keys():
                dist, judge = k
                if max_k[1] > judge: max_k = k
                elif max_k[1] == judge:
                    if max_k[0]*max_k[1] < dist*judge: max_k = k
                    elif max_k[0]*max_k[1] == dist*judge:
                        if max_k[0] < dist: max_k = k
            next_mat = random.choice(next_mat_dict[max_k])
            log_list.append(next_mat)
            mat = next_mat
        return log_list