import random
from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import MutableSequence
from typing import ClassVar


class HashArray(MutableSequence):
    def __init__(
        self,
        array: MutableSequence,
        callback: Callable[[int], None] | None = None,
        hash_map: dict = None,
        bit_size: int = 60,
    ):
        if hash_map is None:
            hash_map = {}
        self._inner = array
        self._callback = callback
        self._hash_map = hash_map
        self._bit_size = bit_size
        self._hash: int = 0

        for i in range(len(self)):
            x = self._inner[i]
            if i not in self._hash_map:
                self._hash_map[i] = {}
            if isinstance(x, Hashable):
                if x not in self._hash_map[i]:
                    self._hash_map[i][x] = random.randrange(1 << self._bit_size)
                self._hash ^= self._hash_map[i][x]
            elif isinstance(x, MutableSequence):
                x = HashArray(x, self.add_hash, self._hash_map[i])
                self._inner[i] = x
            else:
                raise TypeError("Value must be mutable-sequence or hashable")
        if self._callback is not None:
            self._callback(self._hash)

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index):
        return self._inner[index]

    def __setitem__(self, index, value):
        if index < 0:
            index += len(self._inner)
        v = self._inner[index]
        sub = self._hash_map[index][v]
        self._inner[index] = value
        if isinstance(value, Hashable):
            if value not in self._hash_map[index]:
                self._hash_map[index][value] = random.randrange(1 << self._bit_size)
            sub ^= self._hash_map[index][value]
        elif isinstance(value, MutableSequence):
            value = HashArray(value, self.add_hash, self._hash_map[index])
            self._inner[index] = value
        else:
            raise TypeError("Value must be mutable-sequence or hashable")
        self.add_hash(sub)
        if self._callback is not None:
            self._callback(sub)

    def __delitem__(self, index):
        if index < 0:
            index += len(self._inner)
        for i in range(index, len(self) - 1):
            self[i] = self[i + 1]
        v = self._inner[-1]
        self.add_hash(self._hash_map[len(self) - 1][v])
        del self._inner[-1]

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
        self._inner.append(None)
        if index not in self._hash_map:
            self._hash_map[index] = {None: 0}
        self[index] = value

    def get_hash(self):
        return self._hash

    def add_hash(self, value: int):
        self._hash ^= value

    def __repr__(self):
        return self._inner.__repr__()


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

    @classmethod
    def set_zobrist_map(cls, zobrist_map: dict):
        cls._zobrist_map = zobrist_map

    @classmethod
    def get_zobrist_map(cls):
        return cls._zobrist_map

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
