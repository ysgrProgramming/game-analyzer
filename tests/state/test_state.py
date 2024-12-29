import pytest
import random
from dataclasses import dataclass

from game_analyzer import State


@pytest.fixture
def fixed_random_seed():
    random.seed(0)


# ------------------------------------------------------------------------------------
# 1) Hashable のみ
# ------------------------------------------------------------------------------------
@dataclass
class MyStateHashableOnly(State):
    x: int


def test_init_hashable_only(fixed_random_seed):
    st = MyStateHashableOnly(10)
    assert st.x == 10


def test_same_values_hashable_only(fixed_random_seed):
    s1 = MyStateHashableOnly(10)
    s2 = MyStateHashableOnly(10)
    s3 = MyStateHashableOnly(20)
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_element_change_hashable_only(fixed_random_seed):
    st = MyStateHashableOnly(10)
    digest1 = st.digest
    st.x = 20
    digest2 = st.digest
    st.x = 10
    digest3 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3


# ------------------------------------------------------------------------------------
# 2) list のみ (要素は int 等の Hashable を想定し、ネストなし)
# ------------------------------------------------------------------------------------
@dataclass
class MyStateListOnly(State):
    data: list


def test_init_list_only(fixed_random_seed):
    st = MyStateListOnly([1, 2, 3])
    assert list(st.data) == [1, 2, 3]


def test_same_values_list_only(fixed_random_seed):
    s1 = MyStateListOnly([1, 2, 3])
    s2 = MyStateListOnly([1, 2, 3])
    s3 = MyStateListOnly([10, 20, 30])
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_list_change_item(fixed_random_seed):
    st = MyStateListOnly([10, 20, 30])
    digest1 = st.digest
    st.data[1] = 99
    digest2 = st.digest
    st.data[1] = 20
    digest3 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3


def test_list_add_item(fixed_random_seed):
    st = MyStateListOnly([1, 2])
    digest1 = st.digest
    st.data.append(3)
    digest2 = st.digest
    st.data.pop()
    digest3 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3


def test_list_remove_item(fixed_random_seed):
    """del / pop / remove などで要素削除したとき digest が戻るか"""
    st = MyStateListOnly([1, 2, 3])
    digest1 = st.digest
    del st.data[1]  # 2 を削除
    digest2 = st.digest
    # 戻すためには同じ位置に同じ値を insert するとか append するなど
    st.data.insert(1, 2)
    digest3 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3


# ------------------------------------------------------------------------------------
# 3) Mixed: Hashable + list
# ------------------------------------------------------------------------------------
@dataclass
class MyStateMixed(State):
    x: int
    data: list


def test_init_mixed(fixed_random_seed):
    st = MyStateMixed(100, [1, 2, 3])
    assert st.x == 100
    assert list(st.data) == [1, 2, 3]


def test_same_values_mixed(fixed_random_seed):
    s1 = MyStateMixed(10, [1, 2, 3])
    s2 = MyStateMixed(10, [1, 2, 3])
    s3 = MyStateMixed(20, [4, 5, 6])
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_change_hashable_mixed(fixed_random_seed):
    st = MyStateMixed(10, [0, 0])
    digest1 = st.digest
    st.x = 99
    st.data[1] = 1
    digest2 = st.digest
    st.x = 10
    st.data[1] = 0
    digest3 = st.digest
    assert digest1 != digest2
    assert digest1 == digest3


def test_list_add_item_mixed(fixed_random_seed):
    st = MyStateMixed(10, [1, 2])
    digest1 = st.digest
    st.data.append(3)
    digest2 = st.digest
    st.data.pop()
    digest3 = st.digest
    assert digest1 != digest2
    assert digest1 == digest3


def test_list_remove_item_mixed(fixed_random_seed):
    st = MyStateMixed(10, [1, 2, 3])
    digest1 = st.digest
    del st.data[1]  # 2を削除
    digest2 = st.digest
    st.data.insert(1, 2)
    digest3 = st.digest
    assert digest1 != digest2
    assert digest1 == digest3
