from collections import deque


def radix_sort(arr):
    if not arr:
        return arr
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