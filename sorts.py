"""Sort algorithm definitions."""
from dataclasses import dataclass
from typing import Callable

import sort_func


@dataclass
class SortAlg:
    name: str
    time_complexity: str
    space_complexity: str
    is_stable: bool
    sort_function: Callable


BUBBLE = SortAlg(
    name="bubble sort",
    time_complexity="O(n**2)",
    space_complexity="O(1)",
    is_stable=True,
    sort_function=sort_func.bubble_sort,
)
RADIX = SortAlg(
    name="radix sort",
    time_complexity="O(d*(n+k))",
    space_complexity="O(n+k)",
    is_stable=False,
    sort_function=sort_func.radix_sort,
)
BUCKET = SortAlg(
    name="bucket sort",
    time_complexity="O(n)",
    space_complexity="O(n+k)",
    is_stable=False,
    sort_function=sort_func.bucket_sort,
)
COUNTING = SortAlg(
    name="counting sort",
    time_complexity="O(n)",
    space_complexity="O(n+k)",
    is_stable=False,
    sort_function=sort_func.counting_sort,
)
HEAP = SortAlg(
    name="heap sort",
    time_complexity="O(nLogn)",
    space_complexity="O(1)",
    is_stable=False,
    sort_function=sort_func.heap_Sort,
)
INSERTION = SortAlg(
    name="insertion sort",
    time_complexity="O(n**2)",
    space_complexity="O(1)",
    is_stable=True,
    sort_function=sort_func.insertion_sort,
)
SHELL = SortAlg(
    name="shell sort",
    time_complexity="O(n)",
    space_complexity="O(1)",
    is_stable=False,
    sort_function=sort_func.shell_sort,
)
QUICK = SortAlg(
    name="quick sort",
    time_complexity="O(nlogn)",
    space_complexity="O(logn)",
    is_stable=False,
    sort_function=sort_func.qs,
)
MERGE = SortAlg(
    name="merge sort",
    time_complexity="O(nlogn)",
    space_complexity="O(n)",
    is_stable=True,
    sort_function=sort_func.merge_sort,
)

ARRAY_OF_SORTS = [
    BUBBLE,
    RADIX,
    BUCKET,
    COUNTING,
    HEAP,
    INSERTION,
    SHELL,
    QUICK,
    MERGE,
]
