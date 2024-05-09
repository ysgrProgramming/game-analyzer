import numpy as np
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
from dataclasses import dataclass

@dataclass
class Game(ABC):
    init_state: np.ndarray[int]
    range_of_elements: tuple[int, int]
    default_eval: int = 0

    @property
    def shape(self):
        return self.init_state.shape

    @abstractmethod
    def find_next_states(self, state: np.ndarray[int]) -> Generator[Iterable[np.ndarray[int], int | None], None, None]:
        pass
    
    @abstractmethod
    def find_mirror_states(self, state: np.ndarray[int]) -> Generator[np.ndarray[int], None, None]:
        yield state
    
    @abstractmethod
    def evaluate_state(self, state: np.ndarray[int]) -> int | None:
        return None