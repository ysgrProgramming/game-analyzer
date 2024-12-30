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


def test_init_hashable_only(fixed_random_seed):
    @dataclass
    class MyStateHashableOnly(State):
        x: int

    st = MyStateHashableOnly(10)
    assert st.x == 10


def test_same_values_hashable_only(fixed_random_seed):
    @dataclass
    class MyStateHashableOnly(State):
        x: int

    s1 = MyStateHashableOnly(10)
    s2 = MyStateHashableOnly(10)
    s3 = MyStateHashableOnly(20)
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_element_change_hashable_only(fixed_random_seed):
    @dataclass
    class MyStateHashableOnly(State):
        x: int

    st = MyStateHashableOnly(10)
    digest1 = st.digest
    st.x = 20
    digest2 = st.digest
    st.x = 10
    digest3 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3


def test_set_delete_hashable_only(fixed_random_seed):
    @dataclass
    class MyStateHashableOnly(State):
        x: int

    st = MyStateHashableOnly(10)
    digest1 = st.digest
    st.y = 20
    digest2 = st.digest
    del st.y
    digest3 = st.digest
    st.y = 20
    digest4 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3
    assert digest2 == digest4


# ------------------------------------------------------------------------------------
# 2) list のみ (要素は int 等の Hashable を想定し、ネストなし)
# ------------------------------------------------------------------------------------
@dataclass
class MyStateListOnly(State):
    data: list


def test_init_list_only(fixed_random_seed):
    @dataclass
    class MyStateListOnly(State):
        data: list

    st = MyStateListOnly([1, 2, 3])
    assert list(st.data) == [1, 2, 3]


def test_same_values_list_only(fixed_random_seed):
    @dataclass
    class MyStateListOnly(State):
        data: list

    s1 = MyStateListOnly([1, 2, 3])
    s2 = MyStateListOnly([1, 2, 3])
    s3 = MyStateListOnly([10, 20, 30])
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_change_hashable_list_only(fixed_random_seed):
    @dataclass
    class MyStateMixed(State):
        data: list

    st = MyStateMixed([1, 2, 3])
    digest1 = st.digest
    st.data[0] = 10
    digest2 = st.digest
    st.data[0] = 1
    digest3 = st.digest
    assert digest1 != digest2
    assert digest1 == digest3


def test_set_delete_list_only(fixed_random_seed):
    @dataclass
    class MyStateListOnly(State):
        data: list

    st = MyStateListOnly([1, 2, 3])
    digest1 = st.digest
    st.extra_data = [10, 20, 30]
    digest2 = st.digest
    del st.extra_data
    digest3 = st.digest
    st.extra_data = [10, 20, 30]
    digest4 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3
    assert digest2 == digest4


# ------------------------------------------------------------------------------------
# 3) Mixed: Hashable + list
# ------------------------------------------------------------------------------------


def test_init_mixed(fixed_random_seed):
    @dataclass
    class MyStateMixed(State):
        x: int
        data: list

    st = MyStateMixed(100, [1, 2, 3])
    assert st.x == 100
    assert list(st.data) == [1, 2, 3]


def test_same_values_mixed(fixed_random_seed):
    @dataclass
    class MyStateMixed(State):
        x: int
        data: list

    s1 = MyStateMixed(10, [1, 2, 3])
    s2 = MyStateMixed(10, [1, 2, 3])
    s3 = MyStateMixed(20, [4, 5, 6])
    assert s1.digest == s2.digest
    assert s1.digest != s3.digest


def test_change_hashable_mixed(fixed_random_seed):
    @dataclass
    class MyStateMixed(State):
        x: int
        data: list

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


def test_set_delete_mixed(fixed_random_seed):
    @dataclass
    class MyStateMixed(State):
        x: int
        data: list

    st = MyStateMixed(10, [1, 2, 3])
    digest1 = st.digest
    st.y = 20
    st.extra_data = [10, 20, 30]
    digest2 = st.digest
    del st.y
    del st.extra_data
    digest3 = st.digest
    st.y = 20
    st.extra_data = [10, 20, 30]
    digest4 = st.digest

    assert digest1 != digest2
    assert digest1 == digest3
    assert digest2 == digest4


def test_different_subclass(fixed_random_seed):
    @dataclass
    class MyState1(State):
        x: int
        data: list

    @dataclass
    class MyState2(State):
        x: int
        data: list

    st1 = MyState1(10, [1, 2, 3])
    st2 = MyState2(10, [1, 2, 3])

    assert st1.digest != st2.digest
