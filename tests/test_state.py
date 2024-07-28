from game_analyzer import Game
from dataclasses import dataclass
from typing import Hashable

def test_state():
    @dataclass
    class MyState(State):
        a: int
        b: list[list[int]]
        _c: int
    
    matrix = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8]
    ]
    matrixxxxxxx = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 999999999]
    ]
    state = State()
    state1 = MyState(a=1, b=matrix, _c=2)
    state2 = MyState(a=1111111, b=matrix, _c=2)
    state3 = MyState(a=1, b=matrixxxxxxx, _c=2)
    state4 = MyState(a=1, b=matrix, _c=2222222)
    assert isinstance(state, Hashable)
    assert isinstance(state1, Hashable)
    assert hash(state1) != hash(state2)
    assert hash(state1) != hash(state3)
    assert hash(state1) == hash(state4)