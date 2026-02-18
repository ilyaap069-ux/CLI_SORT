from collections import deque
def bubble_sort(arr):
    for j in range(len(arr)):
        for i in range(len(arr) - 1):
            if arr[i] > arr[i+1]:
                arr[i], arr[i+1] = arr[i+1], arr[i]
    return arr

def radix_sort(arr):
    n = max(arr)
    buckets = [deque() for _ in range(10)] #создаём бакеты
    r = 1 #разряд
    while r <= n:
        for x in arr:
            d = (x // r) % 10
            buckets[d].append(x)
        arr = []
        for b in buckets:
            while b:
                arr.append(b.popleft())
        r *= 10
    return arr

def bucket_sort(arr):
    max_val = max(arr)
    bits = [False] * (max_val + 1)
    for x in arr:
        bits[x] = True
    res = []
    for i in range(len(bits)):
        if bits[i]:
            res.append(i)
    return res

def counting_sort(nums):
    bucket = [0] * (max(nums) + 1)
    for num in nums:
        bucket[num] += 1
    res = []
    for i in range(len(bucket)):
        res.extend([i] * bucket[i])
    return res

def heapify(arr, n, i):
    largest = i
    left = 2*i + 1
    right = 2*i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)
    return arr

def heap_Sort(arr):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # Swap max to end
        heapify(arr, i, 0)
    return arr

def insertion_sort(arr):
    # Проходим по всем элементам, начиная со второго
    for i in range(1, len(arr)):
        key = arr[i]  #Текущий элемент для вставки
        idx = i - 1

        # Сдвигаем элементы больше key вправо
        while idx >= 0 and arr[idx] > key:
            arr[idx + 1] = arr[idx]
            idx -= 1

        arr[idx + 1] = key

    return arr

def shell_sort(arr):
    n = len(arr)
    m = n//2
    while m != 0:
        for i in range(m, n):
            idx = i
            while arr[idx - m] > arr[idx] and idx >= m:
                arr[idx - m], arr[idx] = arr[idx], arr[idx - m]
                idx -= m
        m //= 2
    return arr

def qs(arr):
    if len(arr) <= 1:
        return arr
    if len(arr) == 2:
        if arr[0] > arr[1]:
            arr[1], arr[0] = arr[0], arr[1]
    pivot = arr[0]
    ls = []
    rs = []
    for num in arr[1:]:
        if num >= pivot:
            rs.append(num)
        else:
            ls.append(num)
    return qs(ls) + [pivot] + qs(rs)


def merge_sort(arr):
    if not arr or len(arr) == 1:
        return arr
    m = len(arr) // 2
    l_arr = arr[:m]
    r_arr = arr[m:]
    return merge(merge_sort(l_arr), merge_sort(r_arr))

def merge(l_arr, r_arr):
    i = 0
    j = 0
    res = []
    while i < len(l_arr) and j < len(r_arr):
        if l_arr[i] < r_arr[j]:
            res.append(l_arr[i])
            i += 1
        else:
            res.append(r_arr[j])
            j += 1
    res.extend(l_arr[i:])
    res.extend(r_arr[j:])
    return res