from abc import ABC, abstractmethod
from games import Game
from result import Result

class Analyzer(ABC):
    @abstractmethod
    def solve(self, game: Game) -> Result:
        pass