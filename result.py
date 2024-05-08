from dataclasses import dataclass

@dataclass
class Result:
    hash_list: list[int]
    eval_list: list[int]