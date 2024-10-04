from game_analyzer.util import convert_object_to_hashable


class State:
    def to_hash(self):
        return convert_object_to_hashable(self)

