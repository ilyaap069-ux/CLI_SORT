# CLI Sort

CLI Sort started as a terminal program for comparing sorting algorithms and is now also available as a **Telegram bot**.

You can:
- run it from the **command line** (old mode), or
- talk to the **Telegram bot**, send an array or generation parameters, choose an algorithm with buttons and see timing results.

The interface is in Russian; invalid input and errors are handled with clear messages (no tracebacks).

## Telegram bot

### Features

- **Ввод массива** — отправьте сообщение с числами через пробел, например: `5 2 9 1 7`.
- **Генерация массива** — команда `/gen`, затем минимум, максимум и количество, например: `-10 10 5`.
- **Кнопки сортировок** — после получения массива бот показывает кнопки с доступными алгоритмами (counting и bucket скрываются, если есть отрицательные числа).
- **Команда `/sort`** — формат `/sort <алгоритм> <числа...>`, например: `/sort quick 5 3 1 4`.
- **Сравнение времени** — бот выводит время выбранного алгоритма и встроенной сортировки Python.
- **FAQ** — команда `/faq` с краткой справкой.

### Запуск бота локально

1. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

2. Создайте файл `.env` рядом с `bot.py` и добавьте в него токен вашего бота:

   ```env
   TELEGRAM_TOKEN=ваш_токен_бота
   ```

3. Запустите бота:

   ```bash
   python bot.py
   ```

После запуска бот будет работать через `infinity_polling` и обрабатывать команды в Telegram.

## CLI‑режим (старый интерфейс)

В терминале программа работает как меню‑ориентированный CLI.

### Как это работает

1. **Введите или сгенерируйте числа**
   - **0 — Написать массив** — введите целые числа через пробел (например, `5 2 9 1 7`).
   - **1 — Сгенерировать** — задайте минимум, максимум и количество элементов.
2. **Выберите сортировку** — укажите номер алгоритма (0–8). Counting и Bucket предлагаются только для массивов без отрицательных чисел.
3. **Результаты** — выводится отсортированный массив и сравнение времени с встроенной сортировкой Python.
4. **Что дальше?**
   - **0** — ещё раз отсортировать этот же массив (можно другим алгоритмом).
   - **1** — ввести или сгенерировать новый массив.
   - **2** — выйти из программы.

### Доступные алгоритмы сортировки

| # | Algorithm      | Time        | Space   |
|---|----------------|------------|---------|
| 0 | Bubble sort    | O(n²)      | O(1)    |
| 1 | Radix sort     | O(d×(n+k)) | O(n+k)  |
| 2 | Bucket sort    | O(n+k)     | O(n+k)  |
| 3 | Counting sort  | O(n+k)     | O(n+k)  |
| 4 | Heap sort      | O(n log n) | O(1)    |
| 5 | Insertion sort | O(n²)      | O(1)    |
| 6 | Shell sort     | O(n²)      | O(1)    |
| 7 | Quick sort     | O(n log n) | O(log n)|
| 8 | Merge sort     | O(n log n) | O(n)    |

**Примечание:** Bucket sort и Counting sort поддерживают только неотрицательные целые числа; при наличии отрицательных элементов они не предлагаются.

## Запуск CLI‑версии

```bash
python main.py
```

## Requirements

- Python 3.x
