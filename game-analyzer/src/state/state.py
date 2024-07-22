from abc import ABC
from ..util import convert_statedict_to_hashable

class State(ABC):
    def __hash__(self) -> int:
        return hash(convert_statedict_to_hashable(self.__getstate__().items()))