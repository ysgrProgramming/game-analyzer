from typing import ClassVar
from collections.abc import Hashable, Iterable
import random

class State:
    _zobrist_map: ClassVar[dict] = {}
    _rand_bit_size: ClassVar[int] = 64

    def to_hash(self) -> int:
        state_dict = self.to_dict()
        if self._zobrist_map == {}:
            self._init_zobrist_map(state_dict, self._zobrist_map)
        h = 0
        for k, v in state_dict.items():
            h ^= self._get_zobrist_hash(v, self._zobrist_map[k])
        return h

    def to_dict(self) -> dict:
        return self.__dict__

    def _get_zobrist_hash(self, obj, mapping) -> int:  # noqa: C901
        if isinstance(obj, Hashable):
            if obj not in mapping:
                mapping[obj] = random.randrange(1<<self._rand_bit_size)  # noqa: S311
            return mapping[obj]
        if isinstance(obj, Iterable):
            h = 0
            for v, m in zip(obj, mapping, strict=True):
                h ^= self._get_zobrist_hash(v, m)
            return h
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)

    def _init_zobrist_map(self, obj, mapping):  # noqa: C901
        if isinstance(obj, Hashable):
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                mapping[k] = {}
                self._init_zobrist_map(v, mapping[k])
            return
        if isinstance(obj, Iterable):
            mapping = [{} for _ in range(len(obj))] # type: ignore
            for v, m in zip(obj, mapping, strict=True):
                self._init_zobrist_map(v, m)
            return
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)
