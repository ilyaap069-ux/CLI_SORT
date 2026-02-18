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
    sort_function=sort_func.qs)

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
    minim = int(input("Введите минимальное число для генератора: "))
    maxim = int(input("Введите максимальное число для генератора: "))
    count = int(input("Введите количество чисел в массиве: "))
    arr = [randint(minim, maxim) for _ in range(count)]
    print("Получившийся массив: ", arr)
    return arr


def sort_result(SortAlg, arr):
    new_arr = arr.copy()
    print("Название:", SortAlg.name)
    print("time complexity:", SortAlg.time_complexity)
    print("space complexity:", SortAlg.space_complexity)
    start = time.perf_counter()
    res = SortAlg.sort_function(arr)
    end = time.perf_counter()
    d1 = f"{(end - start) * 1000:.4f}"


    start = time.perf_counter()
    cor_arr = sorted(arr)
    end = time.perf_counter()
    d2 = f"{(end - start) * 1000:.4f}"


    if res != cor_arr and SortAlg != BUCKET:
        raise ValueError("Результат не корректен")

    return d1, d2, res


def main_body(array_of_sorts, arr):
    n = len(array_of_sorts)
    print("С помощью чего отсортировать массив:")
    for i in range(n):
        print(f"{i}.{array_of_sorts[i].name}")
    lvl = int(input("ведите номер сортировки >>> "))
    if lvl > len(array_of_sorts) or lvl < 0:
        print("Нет такого номера. Попробуйте ещё раз")
    d1, d2, res = sort_result(array_of_sorts[lvl], arr)
    print(f"Время нашей сортировки:     {d1} мс"
          f"\nВремя системной сортировки: {d2} мс"
          f"\nИтоговый массив: {res}")


ch = True
print("Привет Пользователь! \nЭто программа, для сравнения сортировок")
while ch:
    check = True
    while check:
        gen = int(input("Вы хотите написать массив или сгенерировать? \n0.Написать массив \n1.Сгенерировать \nВведите здесь >>> "))
        if gen == 0:
            arr = list(map(int, input("Введите ваш массив без скобок, через пробел >>> ").split()))
        elif gen == 1:
            arr = array_generator()
            if not ch:
                break
            main_body(array_of_sorts, arr)


            print("Что делать дальше?")
            a = int(input("0.Отсортировать этот же массив \n1.Ввести другой массив \n2.Выйти из программы \nВведите номер: "))
            if a == 0:
                continue
            if a == 1:
                check = False
                continue
            if a == 2:
                ch = False
                continue

print("Спасибо за использование!")