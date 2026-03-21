import pytest
from sort_func import (
    bubble_sort,
    bucket_sort,
    counting_sort,
    radix_sort,
    heap_Sort,
    insertion_sort,
    shell_sort,
    qs,
    merge_sort,
)


SIMPLE_CASES = [
    ([5, 3, 8, 1, 2], [1, 2, 3, 5, 8]),
    ([1], [1]),
    ([2, 1], [1, 2]),
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
    ([3, 3, 1, 1, 2, 2], [1, 1, 2, 2, 3, 3]),
]

ALL_SORTS = [
    bubble_sort,
    insertion_sort,
    shell_sort,
    qs,
    merge_sort,
    heap_Sort,
]

# Эти алгоритмы работают только с неотрицательными целыми
NON_NEGATIVE_SORTS = [
    counting_sort,
    radix_sort,
]

NON_NEGATIVE_WITH_DUPES = [
    bucket_sort,
]


@pytest.mark.parametrize("sort_fn", ALL_SORTS, ids=lambda fn: fn.__name__)
@pytest.mark.parametrize("input_arr, expected", SIMPLE_CASES, ids=lambda x: str(x))
def test_general_sorts(sort_fn, input_arr, expected):
    result = sort_fn(list(input_arr))
    assert result == expected


@pytest.mark.parametrize("sort_fn", NON_NEGATIVE_SORTS, ids=lambda fn: fn.__name__)
@pytest.mark.parametrize("input_arr, expected", SIMPLE_CASES, ids=lambda x: str(x))
def test_non_negative_sorts(sort_fn, input_arr, expected):
    result = sort_fn(list(input_arr))
    assert result == expected


@pytest.mark.parametrize("sort_fn", NON_NEGATIVE_WITH_DUPES, ids=lambda fn: fn.__name__)
@pytest.mark.parametrize("input_arr, expected", SIMPLE_CASES, ids=lambda x: str(x))
def test_bucket_sort(sort_fn, input_arr, expected):
    result = sort_fn(list(input_arr))
    assert result == expected
