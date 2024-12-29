import random
from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import MutableSequence


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
            self._inner = array._inner
        else:
            self._inner = array
        self._callback = callback
        self._digest_map = digest_map
        self._bit_size = bit_size
        self._digest: int = 0

        for i in range(len(self)):
            value = self._inner[i]
            self.digest_value(i, value)

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index):
        return self._inner[index]

    def __setitem__(self, index, value):
        if index < 0:
            index += len(self._inner)
        digest = self.get_digest(index)
        self.add_digest(digest)
        self._inner[index] = value
        self.digest_value(index, value)

    def __delitem__(self, index):
        if index < 0:
            index += len(self._inner)
        for i in range(index, len(self) - 1):
            self[i] = self[i + 1]
        digest = self.get_digest(len(self) - 1)
        self.add_digest(digest)
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
        self.digest_value(index, value)

    @property
    def digest(self):
        return self._digest

    def get_digest(self, index):
        value = self._inner[index]
        if isinstance(value, HashArray):
            return value.digest
        if isinstance(value, Hashable):
            return self._digest_map[index][value]
        else:
            raise TypeError("Value must be hasharray or digestable")

    def digest_value(self, index, value):
        if index not in self._digest_map:
            self._digest_map[index] = {}
        if isinstance(value, Hashable):
            if value not in self._digest_map[index]:
                self._digest_map[index][value] = random.randrange(1 << self._bit_size)
            self.add_digest(self._digest_map[index][value])
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self.add_digest, self._digest_map[index])
            self._inner[index] = value
        else:
            raise TypeError("Value must be mutable-sequence or digestable")

    def add_digest(self, value: int):
        self._digest ^= value
        if self._callback is not None:
            self._callback(value)

    def __repr__(self):
        return self._inner.__repr__()
