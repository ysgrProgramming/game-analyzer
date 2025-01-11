import random
from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class State:
    __hash__ = None
    _digest_map: ClassVar[dict] = {}
    _bit_size: ClassVar[int] = 60

    def __init_subclass__(cls) -> None:
        cls._digest_map = {}
        cls._bit_size = 60

    @property
    def digest(self) -> int:
        if self._digest_map == {}:
            self._init_digest_map(self.to_dict(), self._digest_map)
        h = 0
        for k in self.__dict__.keys():
            h ^= self._get_obj_digest(getattr(self, k), self._digest_map[k])
        return h

    def to_dict(self) -> dict:
        return self.__dict__

    def _get_obj_digest(self, obj, mapping) -> int:  # noqa: C901
        if isinstance(obj, Hashable):
            if obj not in mapping:
                mapping[obj] = random.randrange(1 << self._bit_size)  # noqa: S311
            return mapping[obj]
        if isinstance(obj, Iterable):
            h = 0
            for v, m in zip(obj, mapping, strict=True):
                h ^= self._get_obj_digest(v, m)
            return h
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)

    def _init_digest_map(self, obj, mapping):  # noqa: C901
        if isinstance(obj, Hashable):
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                mapping[k] = {}
                self._init_digest_map(v, mapping[k])
            return
        if isinstance(obj, Iterable):
            mapping = [{} for _ in range(len(obj))]  # type: ignore
            for v, m in zip(obj, mapping, strict=True):
                self._init_digest_map(v, m)
            return
        msg = "Unsupported type for zobrist hashing"
        raise TypeError(msg)
