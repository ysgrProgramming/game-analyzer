import random
from collections.abc import Callable, Hashable, MutableSequence
from dataclasses import dataclass

from .state import State


class HashArray(MutableSequence):
    __hash__ = None  # type: ignore

    def __init__(
        self,
        array: MutableSequence,
        callback: Callable[[int], None] | None = None,
        digest_map: dict | None = None,
        bit_size: int = 60,
    ):
        if digest_map is None:
            digest_map = {}
        if isinstance(array, HashArray):
            self._inner = array._inner  # noqa: SLF001
        else:
            self._inner = array
        self._callback = callback
        self._digest_map = digest_map
        self._bit_size = bit_size
        self._digest: int = 0

        for i in range(len(self)):
            value = self._inner[i]
            self._digest_value(i, value)

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index):
        return self._inner[index]

    def __setitem__(self, index, value):
        if index < 0:
            index += len(self._inner)
        digest = self._get_digest(index)
        self._add_digest(digest)
        self._inner[index] = value
        self._digest_value(index, value)

    def __delitem__(self, index):
        if index < 0:
            index += len(self._inner)
        for i in range(index, len(self) - 1):
            self[i] = self[i + 1]
        digest = self._get_digest(len(self) - 1)
        self._add_digest(digest)
        del self._inner[len(self) - 1]

    def insert(self, index, value):
        if index < 0:
            index += len(self._inner)
        buf = value
        for i in range(index, len(self)):
            v = self[i]
            self[i] = buf
            buf = v
        self.append(buf)

    def append(self, value):
        index = len(self)
        self._inner.append(value)
        self._digest_value(index, value)

    @property
    def digest(self):
        return self._digest

    def _get_digest(self, index):
        value = self._inner[index]
        if isinstance(value, Hashable):
            return self._digest_map[index][value]
        if isinstance(value, HashArray):
            return value.digest
        raise TypeError("Value must be hasharray or digestable")

    def _digest_value(self, index, value):
        if index not in self._digest_map:
            self._digest_map[index] = {}
        if isinstance(value, Hashable):
            if value not in self._digest_map[index]:
                self._digest_map[index][value] = random.randrange(1 << self._bit_size)
            self._add_digest(self._digest_map[index][value])
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self._add_digest, self._digest_map[index])
            self._inner[index] = value
        else:
            raise TypeError("Value must be mutable-sequence or digestable")

    def _add_digest(self, value: int):
        self._digest ^= value
        if self._callback is not None:
            self._callback(value)

    def __repr__(self):
        return self._inner.__repr__()


@dataclass
class HashState(State):
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
