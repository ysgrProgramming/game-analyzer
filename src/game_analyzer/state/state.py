import random
from collections.abc import Hashable
from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar


@dataclass(slots=True)
class State:
    _zobrist_map: ClassVar[dict] = {}
    _rand_bit_size: ClassVar[int] = 60

    def to_hash(self) -> int:
        if self._zobrist_map == {}:
            self._init_zobrist_map(self.to_dict(), self._zobrist_map)
        h = 0
        for k in self.__slots__:
            h ^= self._get_zobrist_hash(getattr(self, k), self._zobrist_map[k])
        return h

    def to_dict(self) -> dict:
        d = {}
        for k in self.__slots__:
            d[k] = getattr(self, k)
        return d

    def _get_zobrist_hash(self, obj, mapping) -> int:  # noqa: C901
        if isinstance(obj, Hashable):
            if obj not in mapping:
                mapping[obj] = random.randrange(1 << self._rand_bit_size)  # noqa: S311
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
            mapping = [{} for _ in range(len(obj))]  # type: ignore
            for v, m in zip(obj, mapping, strict=True):
                self._init_zobrist_map(v, m)
            return
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)
