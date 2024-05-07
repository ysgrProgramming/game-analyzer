from typing import Iterable
from dataclasses import dataclass

@dataclass
class Result:
    hash_list: list[int]
    hash_dict: dict[int, int]
    eval_list: list[int]