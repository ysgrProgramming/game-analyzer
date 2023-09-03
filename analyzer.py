import numpy as np 
from collections import deque
import random

class Analyzer():
    def __init__(self, init_mat, max_mat, next_func, sym_func, end_func):
        self.dim = len(init_mat.shape)
        self.init_mat = init_mat
        self.max_mat = max_mat
        if self.init_mat.shape != self.max_mat.shape:
            raise Exception("init_mat and max_mat shape mismatched")
        
        self.base1_mat, self.base2_mat = self._create_base_mat(max_mat)
        self.max_hash = np.max(self.base2_mat)

        self.next_func = next_func
        self.sym_func = sym_func
        self.end_func = end_func

        self.graph = None
        self.graph_inv = None
        self.hash_list = None
        self.hash_dict = None
        self.dist_mat = None

    def _create_base_mat(self, max_mat):
        s = max_mat.shape
        flat_mat = max_mat.ravel()
        ac_list = [1]
        for num in flat_mat:
            ac_list.append(num*ac_list[-1])
        ac_mat = np.array(ac_list)

        base1_mat = ac_mat[:-1].reshape(s)
        base2_mat = ac_mat[1:].reshape(s)

        return base1_mat, base2_mat
    
    def mat_to_hash(self, mat):
        hash = np.sum(mat * self.base1_mat)
        return hash
    
    def hash_to_mat(self, hash):
        mat = hash % self.base2_mat // self.base1_mat
        return mat

    def _mat_to_min_hash(self, mat):
        hash = self.max_hash
        for sym_mat in self.sym_func(mat):
            hash = min(hash, self.mat_to_hash(sym_mat))
            if hash in self.hash_dict: return hash
        return hash

    def construct_game_graph(self):
        init_hash = self.mat_to_hash(self.init_mat)
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
                next_hash = self._mat_to_min_hash(next_mat)
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
    
    def make_tree(self):
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
    
    def next(self, now_mat):
        next_mat_dict = dict()
        for next_mat in self.next_func(now_mat):
            next_hash = self._mat_to_min_hash(next_mat)
            next_ind = self.hash_dict[next_hash]
            dist = self.dist_mat[next_ind]
            judge = self.judge_mat[next_ind]
            if (dist, judge) in next_mat_dict:
                next_mat_dict[(dist, judge)] += next_mat
            else:
                next_mat_dict[(dist, judge)] = [next_mat]
        return next_mat_dict
    
    def example(self, ind):
        if type(self.dist_mat) == None: raise Exception("make tree before example")
        hash = self.hash_list[ind]
        mat = self.hash_to_mat(hash)

        log_list = [mat]
        while self.end_func(mat) == None:
            next_mat_dict = self.next(mat)
            max_k = (0, 1)
            for k in next_mat_dict.keys():
                dist, judge = k
                if max_k[1] > judge: max_k = k
                elif max_k[0]*max_k[1] < dist*judge: max_k = k
                elif max_k[0] < dist: max_k = k
            print(next_mat_dict)
            next_mat = random.choice(next_mat_dict[max_k])
            log_list.append(next_mat)
            mat = next_mat
        return log_list