import random
from collections.abc import Hashable, MutableSequence
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
        h = 0
        for k, v in self.to_dict().items():
            if k not in self._digest_map:
                self._digest_map[k] = {}
            h ^= self._get_obj_digest(v, self._digest_map[k])
        return h

    def to_dict(self) -> dict:
        return self.__dict__

    def _get_obj_digest(self, obj, mapping) -> int:
        if isinstance(obj, Hashable):
            if obj not in mapping:
                mapping[obj] = random.randrange(1 << self._bit_size)
            return mapping[obj]
        if isinstance(obj, MutableSequence):
            h = 0
            for i, v in enumerate(obj):
                if i not in mapping:
                    mapping[i] = {}
                h ^= self._get_obj_digest(v, mapping[i])
            return h
        raise TypeError("Value must be mutable-sequence or digestable")
