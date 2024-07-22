from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from ..state import State

@dataclass
class Game(ABC):
    init_state: State
    default_eval: int = 0

    @abstractmethod
    def find_next_states(self, state: State) -> Generator[State, None, None]:
        pass
    
    @abstractmethod
    def find_mirror_states(self, state: State) -> Generator[State, None, None]:
        yield state
    
    @abstractmethod
    def evaluate_state(self, state: State) -> int | None:
        return None