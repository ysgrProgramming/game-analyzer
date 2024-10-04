from dataclasses import dataclass

@dataclass
class Result:
    hash_dict: dict[int, int]
    eval_list: list[int]
