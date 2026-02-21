"""Sort config and logic."""
import time
from random import randint

from sorts import ARRAY_OF_SORTS, BUCKET, COUNTING


def array_generator():
    """Generate random array. Returns list or None on error."""
    try:
        minim = int(input("Введите минимальное число для генератора: "))
        maxim = int(input("Введите максимальное число для генератора: "))
        count = int(input("Введите количество чисел в массиве: "))
    except ValueError:
        return None
    try:
        arr = [randint(minim, maxim) for _ in range(count)]
    except Exception:
        return None
    print("Получившийся массив: ", arr)
    return arr


def sort_result(sort_alg, arr):
    """Run sort, validate, return (d1, d2, res). Raises on invalid result."""
    new_arr = arr.copy()
    print("Название:", sort_alg.name)
    print("time complexity:", sort_alg.time_complexity)
    print("space complexity:", sort_alg.space_complexity)

    start = time.perf_counter()
    res = sort_alg.sort_function(new_arr)
    end = time.perf_counter()
    d1 = f"{(end - start) * 1000:.4f}"

    start = time.perf_counter()
    cor_arr = sorted(arr)
    end = time.perf_counter()
    d2 = f"{(end - start) * 1000:.4f}"

    if res != cor_arr and sort_alg != BUCKET:
        raise ValueError("Результат не корректен")
    return d1, d2, res


def run_sort(sorts_list, arr):
    """Pick sort, run it. Returns True on success."""
    try:
        n = len(sorts_list)
        print("С помощью чего отсортировать массив:")
        for i in range(n):
            print(f"{i}.{sorts_list[i].name}")
        lvl = int(input("Введите номер сортировки >>> "))
    except ValueError:
        return False, "введите целый номер сортировки."

    if lvl >= len(sorts_list) or lvl < 0:
        return False, "Нет такого номера. Попробуйте ещё раз"

    try:
        d1, d2, res = sort_result(sorts_list[lvl], arr)
        print(
            f"Время нашей сортировки:     {d1} мс"
            f"\nВремя системной сортировки: {d2} мс"
            f"\nИтоговый массив: {res}")
        return True, None
    except ValueError as e:
        return False, str(e)
    except Exception:
        return False, "Произошла ошибка при сортировке. Попробуйте другой массив или алгоритм."