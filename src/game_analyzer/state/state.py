from typing import ClassVar
from collections.abc import Hashable, Iterable
import random

class State:
    _zobrist_map: ClassVar[dict] = {}
    _rand_bit_size: ClassVar[int] = 64

    def to_hash(self) -> int:
        state_dict = self.to_dict()
        return self._zobrist_hash(state_dict)

    def to_dict(self) -> dict:
        return self.__dict__

    def _zobrist_hash(self, obj) -> int:
        if isinstance(obj, Hashable):
            return self._get_zobrist_value(obj)
        if isinstance(obj, Iterable):
            h = 0
            for v in obj:
                h ^= self._zobrist_hash(v)
            return h
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)

    def _get_zobrist_value(self, key):
        if key not in self._zobrist_map:
            self._zobrist_map[key] = random.randrange(1<<self._rand_bit_size)  # noqa: S311
        return self._zobrist_map[key]
