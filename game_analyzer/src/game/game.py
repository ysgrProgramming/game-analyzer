from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from ..state import State
from typing import Literal, Generic, TypeVar

T = TypeVar('T')

@dataclass
class Game(ABC, Generic[T]):
    init_state: T
    default_eval: int = 0

    @abstractmethod
    def find_next_states(self, state: T) -> Generator[T, None, None]:
        pass
    
    @abstractmethod
    def find_mirror_states(self, state: T) -> Generator[T, None, None]:
        yield state
    
    @abstractmethod
    def evaluate_state(self, state: T) -> Literal[-1, 0, 1] | None:
        return None