import random
from collections.abc import Hashable, MutableSequence
from dataclasses import dataclass
from typing import ClassVar

from .hash_array import HashArray


@dataclass
class State:
    __hash__ = None  # type: ignore
    _digest_map: ClassVar[dict] = {}
    _bit_size: ClassVar[int] = 60

    def __init_subclass__(cls) -> None:
        cls._digest_map = {}
        cls._bit_size = 60

    def __setattr__(self, name: str, value) -> None:
        if not name.startswith("_"):
            if hasattr(self, name):
                digest = self._get_digest(name)
                self._add_digest(digest)
            super().__setattr__(name, value)
            self._digest_value(name, value)
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if not name.startswith("_"):
            digest = self._get_digest(name)
            self._add_digest(digest)
        super().__delattr__(name)

    def _get_digest(self, name: str):
        value = getattr(self, name)
        if isinstance(value, Hashable):
            return self._digest_map[name][value]
        if isinstance(value, HashArray):
            return value.digest
        raise TypeError("Value must be hasharray or digestable")

    def _digest_value(self, name: str, value):
        if name not in self._digest_map:
            self._digest_map[name] = {}
        if isinstance(value, Hashable):
            if value not in self._digest_map[name]:
                self._digest_map[name][value] = random.randrange(1 << self._bit_size)
            self._add_digest(self._digest_map[name][value])
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self._add_digest, self._digest_map[name])
            super().__setattr__(name, value)
        else:
            raise TypeError("Value must be mutable-sequence or digestable")

    def _add_digest(self, value: int):
        if not hasattr(self, "_digest"):
            self._digest = 0
        self._digest ^= value

    @property
    def digest(self):
        return self._digest
