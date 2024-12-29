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


def test_different_digest(fixed_random_seed):
    arr = [1, 2, 3]
    ha1 = HashArray(arr)
    ha2 = HashArray(arr)
    ha3 = HashArray(ha1)
    assert ha1.digest != ha2.digest
    assert ha1.digest != ha3.digest


def test_different_digest_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    ha1 = HashArray(arr)
    ha2 = HashArray(arr)
    ha3 = HashArray(ha1)
    assert ha1.digest != ha2.digest
    assert ha1.digest != ha3.digest


def test_append_and_pop(fixed_random_seed):
    arr = [1, 2]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha.append(3)
    hash2 = ha.digest
    ha.pop()
    hash3 = ha.digest
    ha.append(3)
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4


def test_setitem(fixed_random_seed):
    arr = [10, 20, 30]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha[1] = 50
    hash2 = ha.digest
    ha[1] = 20
    hash3 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3


def test_insert_and_del(fixed_random_seed):
    arr = [20, 30, 40]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha.insert(0, 10)
    hash2 = ha.digest
    del ha[0]
    hash3 = ha.digest
    ha.insert(0, 10)
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4


def test_append_and_pop_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha[2].append(8)
    hash2 = ha.digest
    ha[2].pop()
    hash3 = ha.digest
    ha[2].append(8)
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4


def test_setitem_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha[1][1] = 50
    hash2 = ha.digest
    ha[1][1] = 4
    hash3 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3


def test_insert_and_del_nested(fixed_random_seed):
    arr = [[0, 1, 2], [4, 5], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha[1].insert(0, 3)
    hash2 = ha.digest
    del ha[1][0]
    hash3 = ha.digest
    ha[1].insert(0, 3)
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4


def test_append_and_pop_array_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha.append([6, 7, 8])
    hash2 = ha.digest
    ha.pop()
    hash3 = ha.digest
    ha.append([6, 7, 8])
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4


def test_setitem_array_nested(fixed_random_seed):
    arr = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha[1] = [10, 10, 10, 10]
    hash2 = ha.digest
    ha[1] = [3, 4, 5]
    hash3 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3


def test_insert_and_del_array_nested(fixed_random_seed):
    arr = [[0, 1, 2], [6, 7, 8]]
    ha = HashArray(arr)
    hash1 = ha.digest
    ha.insert(1, [3, 4, 5])
    hash2 = ha.digest
    del ha[1]
    hash3 = ha.digest
    ha.insert(1, [3, 4, 5])
    hash4 = ha.digest
    assert hash1 != hash2
    assert hash1 == hash3
    assert hash2 == hash4
