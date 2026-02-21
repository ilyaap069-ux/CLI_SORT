# CLI Sort

A command-line tool for sorting numbers. Enter your numbers (or generate them randomly), pick a sorting algorithm, and get your array sorted. The interface is in Russian; invalid input and errors are handled with clear messages (no tracebacks).

## How it works

1. **Enter or generate numbers**
   - **0 — Написать массив** — Type integers separated by spaces (e.g. `5 2 9 1 7`).
   - **1 — Сгенерировать** — Generate a random array by entering min value, max value, and count.
2. **Pick a sort** — Choose a sorting algorithm by number (0–8). Counting and Bucket sort are only offered when all numbers are non-negative.
3. **See results** — Get the sorted array and a timing comparison with Python’s built-in sort.
4. **What next?**
   - **0** — Sort the same array again (possibly with another algorithm).
   - **1** — Enter or generate a new array.
   - **2** — Exit the program.

## Available sorting algorithms

| # | Algorithm     | Time        | Space   |
|---|---------------|-------------|---------|
| 0 | Bubble sort   | O(n²)       | O(1)    |
| 1 | Radix sort    | O(d×(n+k))  | O(n+k)  |
| 2 | Bucket sort   | O(n)        | O(n+k)  |
| 3 | Counting sort | O(n)        | O(n+k)  |
| 4 | Heap sort     | O(n log n)  | O(1)    |
| 5 | Insertion sort| O(n²)       | O(1)    |
| 6 | Shell sort    | O(n)        | O(1)    |
| 7 | Quick sort    | O(n log n)  | O(log n)|
| 8 | Merge sort    | O(n log n)  | O(n)    |

**Note:** Bucket sort and Counting sort support only non-negative integers; they are hidden when the array contains negative numbers.

## Error handling

- Invalid numeric input (e.g. letters, wrong format) shows a short error message and asks again.
- Invalid algorithm number or sort failure shows a message; you can pick another algorithm or array.
- Unexpected errors are caught so the program does not crash; you can continue using it.

## Run it

```bash
python main.py
```

## Requirements

- Python 3.x
