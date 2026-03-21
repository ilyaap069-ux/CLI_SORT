from collections import deque
from typing import Iterable, List


def bubble_sort(arr: List[int]) -> List[int]:
    """Простая сортировка пузырьком (in‑place, устойчивая)."""
    n = len(arr)
    for pass_index in range(n):
        # После каждого прохода самый большой элемент "всплывает" в конец
        for i in range(0, n - 1 - pass_index):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return arr


def radix_sort(arr: List[int]) -> List[int]:
    """Radix sort для неотрицательных целых чисел."""
    if not arr:
        return []
    if any(value < 0 for value in arr):
        raise ValueError("radix_sort поддерживает только неотрицательные числа")

    result = list(arr)
    max_value = max(result)
    digit_place = 1  # 1, 10, 100, ...

    while max_value // digit_place > 0:
        buckets = [deque() for _ in range(10)]

        for number in result:
            digit = (number // digit_place) % 10
            buckets[digit].append(number)

        result = []
        for bucket in buckets:
            while bucket:
                result.append(bucket.popleft())

        digit_place *= 10

    return result


def bucket_sort(arr: List[int]) -> List[int]:
    """Bucket сортировка для неотрицательных целых чисел (с поддержкой дубликатов)."""
    if not arr:
        return []
    if any(value < 0 for value in arr):
        raise ValueError("bucket_sort поддерживает только неотрицательные числа")

    max_value = max(arr)
    counts = [0] * (max_value + 1)

    for value in arr:
        counts[value] += 1

    result: List[int] = []
    for value, count in enumerate(counts):
        if count:
            result.extend([value] * count)

    return result


def counting_sort(arr: List[int]) -> List[int]:
    """Counting sort для неотрицательных целых чисел."""
    if not arr:
        return []
    if any(value < 0 for value in arr):
        raise ValueError("counting_sort поддерживает только неотрицательные числа")

    max_value = max(arr)
    counts = [0] * (max_value + 1)

    for value in arr:
        counts[value] += 1

    result: List[int] = []
    for value, count in enumerate(counts):
        if count:
            result.extend([value] * count)

    return result


def heapify(arr: List[int], heap_size: int, root_index: int) -> List[int]:
    """Просеивание вниз одного узла кучи (in‑place)."""
    largest_index = root_index
    left_child = 2 * root_index + 1
    right_child = 2 * root_index + 2

    if left_child < heap_size and arr[left_child] > arr[largest_index]:
        largest_index = left_child
    if right_child < heap_size and arr[right_child] > arr[largest_index]:
        largest_index = right_child

    if largest_index != root_index:
        arr[root_index], arr[largest_index] = arr[largest_index], arr[root_index]
        heapify(arr, heap_size, largest_index)

    return arr


def heap_Sort(arr: List[int]) -> List[int]:
    """Heap sort (in‑place, неустойчивая)."""
    n = len(arr)

    # Строим max‑кучу
    for index in range(n // 2 - 1, -1, -1):
        heapify(arr, n, index)

    # Последовательно выносим максимум в конец массива
    for end_index in range(n - 1, 0, -1):
        arr[end_index], arr[0] = arr[0], arr[end_index]
        heapify(arr, end_index, 0)

    return arr


def insertion_sort(arr: List[int]) -> List[int]:
    """Сортировка вставками (in‑place, устойчивая)."""
    for current_index in range(1, len(arr)):
        current_value = arr[current_index]
        position = current_index - 1

        # Сдвигаем элементы больше current_value вправо
        while position >= 0 and arr[position] > current_value:
            arr[position + 1] = arr[position]
            position -= 1

        arr[position + 1] = current_value

    return arr


def shell_sort(arr: List[int]) -> List[int]:
    """Сортировка Шелла (in‑place)."""
    n = len(arr)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            current_value = arr[i]
            position = i

            while position >= gap and arr[position - gap] > current_value:
                arr[position] = arr[position - gap]
                position -= gap

            arr[position] = current_value
        gap //= 2

    return arr


def qs(arr: List[int]) -> List[int]:
    """Рекурсивный quick sort (возвращает новый список)."""
    if len(arr) <= 1:
        return list(arr)

    if len(arr) == 2:
        a, b = arr
        return [a, b] if a <= b else [b, a]

    pivot = arr[0]
    left: List[int] = []
    right: List[int] = []

    for value in arr[1:]:
        if value < pivot:
            left.append(value)
        else:
            right.append(value)

    return qs(left) + [pivot] + qs(right)


def merge_sort(arr: List[int]) -> List[int]:
    """Сортировка слиянием (возвращает новый список)."""
    if len(arr) <= 1:
        return list(arr)

    middle = len(arr) // 2
    left_half = arr[:middle]
    right_half = arr[middle:]

    return merge(merge_sort(left_half), merge_sort(right_half))


def merge(left: List[int], right: List[int]) -> List[int]:
    """Слияние двух отсортированных подсписков."""
    left_index = 0
    right_index = 0
    result: List[int] = []

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    if left_index < len(left):
        result.extend(left[left_index:])
    if right_index < len(right):
        result.extend(right[right_index:])

    return result
