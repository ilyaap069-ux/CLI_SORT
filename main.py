from dataclasses import dataclass
from typing import Callable
import time
from random import randint
import sort_func
@dataclass
class SortAlg:
    name: str
    time_complexity: str
    space_complexity: str
    is_stable: bool
    sup_float: bool
    sort_function: Callable

BUBBLE = SortAlg(
    name = "bubble sort",
    time_complexity="O(n**2)",
    space_complexity="O(1)",
    is_stable=True,
    sup_float=True,
    sort_function=sort_func.bubble_sort)
RADIX = SortAlg(
    name = "radix sort",
    time_complexity="O(d*(n+k))",
    space_complexity="O(n+k)",
    is_stable=False,
    sup_float=True,
    sort_function=sort_func.radix_sort)
BUCKET = SortAlg(
    name="bucket sort",
    time_complexity="O(n)",
    space_complexity="O(n+k)",
    is_stable=False,
    sup_float=False,
    sort_function=sort_func.bucket_sort)
COUNTING = SortAlg(
    name="counting sort",
    time_complexity="O(n)",
    space_complexity="O(n+k)",
    is_stable=False,
    sup_float=False,
    sort_function=sort_func.counting_sort)
HEAP = SortAlg(
    name="heap sort",
    time_complexity="O(nLogn)",
    space_complexity="O(1)",
    is_stable=False,
    sup_float=True,
    sort_function=sort_func.heap_Sort)
INSERTION = SortAlg(
    name="insertion sort",
    time_complexity="O(n**2)",
    space_complexity="O(1)",
    is_stable=True,
    sup_float=True,
    sort_function=sort_func.insertion_sort)
SHELL = SortAlg(
    name="shell sort",
    time_complexity="O(n)",
    space_complexity="O(1)",
    is_stable=False,
    sup_float=True,
    sort_function=sort_func.shell_sort)
QUICK = SortAlg(
    name="quick sort",
    time_complexity="O(nlogn)",
    space_complexity="O(logn)",
    is_stable=False,
    sup_float=True,
    sort_function=sort_func.qs)
MERGE = SortAlg(
    name="merge sort",
    time_complexity="O(nlogn)",
    space_complexity="O(n)",
    is_stable=True,
    sup_float=True,
    sort_function=sort_func.merge_sort)

array_of_sorts = [BUBBLE, RADIX, BUCKET, COUNTING, HEAP, INSERTION, SHELL, QUICK, MERGE]
array_of_sup_float_sorts = []
for sort in array_of_sorts:
    if sort.sup_float:
        array_of_sup_float_sorts.append(sort)

def is_gen():
    gen = int(input("Вы хотите написать массив или сгенерировать? \n0.Написать массив \n1.Сгенерировать \nВведите здесь >>> "))
    if gen == 0:
        arr = list(map(float, input("Введите ваш массив без скобок, через пробел >>> ").split()))
        for num in arr:
            if type(num) == "float" or num < 0:
                main_body(array_of_sup_float_sorts, arr)
                continue
    elif gen == 1:
        arr = array_generator()

    return arr

def array_generator():
    try:
        minim = int(input("Введите минимальное число для генератора: "))
        maxim = int(input("Введите максимальное число для генератора: "))
        count = int(input("Введите количество чисел в массиве: "))
    except ValueError:
        print("Ошибка: введите целые числа.")
        return None
    try:
        arr = [randint(minim, maxim) for _ in range(count)]
    except Exception:
        print("Ошибка при генерации массива.")
        return None
    print("Получившийся массив: ", arr)
    return arr


def sort_result(sort_alg, arr):
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


def main_body(array_of_sorts, arr):
    try:
        n = len(array_of_sorts)
        print("С помощью чего отсортировать массив:")
        for i in range(n):
            print(f"{i}.{array_of_sorts[i].name}")
        lvl = int(input("Введите номер сортировки >>> "))
    except ValueError:
        print("Ошибка: введите целый номер сортировки.")
        return
    try:
        if lvl >= len(array_of_sorts) or lvl < 0:
            print("Нет такого номера. Попробуйте ещё раз")
            return
        d1, d2, res = sort_result(array_of_sorts[lvl], arr)
        print(f"Время нашей сортировки:     {d1} мс"
              f"\nВремя системной сортировки: {d2} мс"
              f"\nИтоговый массив: {res}")
    except ValueError as e:
        print("Ошибка:", str(e))
    except Exception:
        print("Произошла ошибка при сортировке. Попробуйте другой массив или алгоритм.")


ch = True
print("Привет Пользователь! \nЭто программа, для сравнения сортировок")
while ch:
    if ch == False:
        break
    try:
        check = True
        try:
            gen = int(input("Вы хотите написать массив или сгенерировать? \n0.Написать массив \n1.Сгенерировать \nВведите здесь >>> "))
        except ValueError:
            print("Ошибка: введите 0 или 1.")
            continue
        if gen == 0:
            try:
                arr = list(map(int, input("Введите ваш массив без скобок, через пробел >>> ").split()))
            except ValueError:
                print("Ошибка: введите числа через пробел, без скобок.")
                continue
        elif gen == 1:
            arr = array_generator()
            if arr is None:
                continue
            if not ch:
                break
        else:
            print("Ошибка: введите 0 или 1.")
            continue
        if not arr:
            print("Ошибка: массив не может быть пустым.")
            continue
        sorts_for_arr = [s for s in array_of_sorts if s not in (COUNTING, BUCKET) or min(arr) >= 0]
        while check:
            main_body(sorts_for_arr, arr)
            print("Что делать дальше?")
            try:
                a = int(input("0.Отсортировать этот же массив \n1.Ввести другой массив \n2.Выйти из программы \nВведите номер: "))
            except ValueError:
                print("Ошибка: введите число 0, 1 или 2.")
                continue
            if a == 0:
                continue
            elif a == 1:
                check = False
                continue
            elif a == 2:
                ch = False
                break
            else:
                print("Нет такого номера. Введите 0, 1 или 2.")
    except Exception:
        print("Произошла непредвиденная ошибка. Попробуйте ещё раз.")
        continue

print("Спасибо за использование!")