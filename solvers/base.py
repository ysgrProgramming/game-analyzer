from abc import ABC, abstractmethod
from games import Game
from result import Result

class Solver(ABC):
    @abstractmethod
    def solve(self, game: Game) -> Result:
        pass