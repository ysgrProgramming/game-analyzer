from dataclasses import dataclass
from game_analyzer import State, Game, Solver
from typing import Literal
from problems.graph import CASE_LIST


@dataclass
class GraphState(State):
    position: int
    confirm: bool
    turn: Literal[0, 1]


class Graph(Game):
    def __init__(self, point_list, edge_list):
        self.point_list = point_list
        self.graph = [[] for _ in range(len(point_list))]
        for u, v in edge_list:
            self.graph[u - 1].append(v - 1)
        self.init_state = GraphState(position=0, confirm=False, turn=0)

    def find_next_states(self, state):
        position = state.position
        turn = state.turn
        next_turn = 1 - state.turn

        state.turn = next_turn
        for node in self.graph[position]:
            state.position = node
            yield state
        state.position = position
        state.confirm = True
        yield state
        state.confirm = False
        state.turn = turn

    def find_mirror_states(self, state):
        yield state

    def evaluate_state(self, state):
        if state.confirm:
            point = self.point_list[state.position]
            if state.turn == 0:
                return point
            return -point
        return None


def test_solver_by_graph():
    for case, ans in CASE_LIST:
        graph = Graph(**case)
        solver = Solver()
        result = solver.solve(graph)
        ev, depth = result.state_to_params(graph.init_state)
        assert ev == ans
