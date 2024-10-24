from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from game_analyzer import State


@dataclass
class Game(ABC):
    init_state: State
    default_eval: int = 0

    @abstractmethod
    def find_next_states(self, state: State) -> Iterable[State]:
        pass

    @abstractmethod
    def find_mirror_states(self, state: State) -> Iterable[State]:
        yield state

    @abstractmethod
    def evaluate_state(self, state: State) -> Literal[-1, 0, 1] | None:
        return None
