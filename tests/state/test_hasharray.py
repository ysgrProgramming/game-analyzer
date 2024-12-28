import pytest
import random

from game_analyzer import HashArray


@pytest.fixture
def fixed_random_seed():
    random.seed(0)


def test_basic_initialization(fixed_random_seed):
    arr = [1, 2, 3]
    ha = HashArray(arr)
    assert len(ha) == 3
    assert ha[0] == 1
    assert ha[1] == 2
    assert ha[2] == 3


def test_append_and_pop(fixed_random_seed):
    arr = [1, 2]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha.append(3)
    hash2 = ha.get_hash()
    ha.pop()
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3


def test_setitem(fixed_random_seed):
    arr = [10, 20, 30]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha[1] = 50
    hash2 = ha.get_hash()
    ha[1] = 20
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3


def test_insert_and_del(fixed_random_seed):
    arr = [20, 30, 40]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha.insert(0, 10)
    hash2 = ha.get_hash()
    del ha[0]
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3


def test_append_and_pop_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7]]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha[2].append(8)
    hash2 = ha.get_hash()
    ha[2].pop()
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3


def test_setitem_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha[1][1] = 50
    hash2 = ha.get_hash()
    ha[1][1] = 4
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3


def test_insert_and_del_nested(fixed_random_seed):
    arr = [[0, 1, 2], [4, 5], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.get_hash()
    ha[1].insert(0, 3)
    hash2 = ha.get_hash()
    del ha[1][0]
    hash3 = ha.get_hash()
    assert hash1 != hash2
    assert hash1 == hash3
