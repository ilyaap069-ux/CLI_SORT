import os
from random import randint
from typing import Dict, List, Set
from datetime import datetime, timedelta
import json
import uuid
import inspect

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

from sort_config import sort_result
from sorts import ARRAY_OF_SORTS, BUCKET, COUNTING, RADIX
import sort_func


# Короткие ключи для алгоритмов сортировки, например: /sort quick 3 1 2
SORT_KEY_MAP = {alg.name.split()[0].lower(): alg for alg in ARRAY_OF_SORTS}

# Краткие текстовые описания алгоритмов для показа вместе с кодом
ALGO_DESCRIPTIONS: Dict[str, str] = {
    "bubble": (
        "Пузырьковая сортировка многократно проходит по массиву и "
        "попарно меняет местами соседние элементы, если они стоят "
        "неправильно. После каждого прохода самый большой элемент "
        "\"всплывает\" в конец массива."
    ),
    "radix": (
        "Radix sort сортирует числа по разрядам: сначала по младшему "
        "разряду, затем по следующему и так далее. На каждом шаге "
        "используется стабильная сортировка по одной цифре."
    ),
    "bucket": (
        "Bucket sort для целых неотрицательных чисел создаёт вспомогательный "
        "массив булевых значений (битовую карту) и отмечает, какие числа "
        "встречаются. Затем восстанавливает отсортированный список по этой карте."
    ),
    "counting": (
        "Counting sort считает, сколько раз каждое значение встречается "
        "в массиве, а затем по этим подсчётам восстанавливает отсортированный "
        "массив. Хорошо работает, когда диапазон значений невелик."
    ),
    "heap": (
        "Heap sort сначала строит из массива двоичную кучу (max‑heap), "
        "где на вершине всегда максимальный элемент. Затем по одному "
        "вынимает максимум в конец массива и восстанавливает свойство кучи."
    ),
    "insertion": (
        "Сортировка вставками идёт по массиву слева направо и поддерживает "
        "левую часть в отсортированном состоянии. Для каждого нового элемента "
        "она находит среди уже отсортированных элементов позицию, куда его нужно "
        "вставить, сдвигая более крупные значения вправо. Особенно эффективна, "
        "когда массив почти отсортирован."
    ),
    "shell": (
        "Сортировка Шелла обобщает сортировку вставками: сначала сортируются "
        "элементы на больших расстояниях (шаг gap), затем шаг уменьшается до 1. "
        "Это позволяет быстрее разнести элементы на нужные позиции."
    ),
    "quick": (
        "Быстрая сортировка (quick sort) выбирает опорный элемент (pivot), "
        "делит массив на элементы меньше и не меньше опорного, рекурсивно "
        "сортирует две части и склеивает результат."
    ),
    "merge": (
        "Сортировка слиянием рекурсивно делит массив пополам, сортирует "
        "каждую половину, а затем аккуратно сливает два отсортированных "
        "подмассива в один."
    ),
}

# Путь к файлу логов рядом с исходниками, независимо от текущей рабочей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs.jsonl")

# Чаты, для которых мы ждём параметры генерации (min max count)
GENERATION_AWAITING_PARAMS: Set[int] = set()

# Последний исходный массив пользователя (по chat_id)
LAST_ARRAY_BY_CHAT: Dict[int, List[int]] = {}

# Последний отсортированный массив (результат) по chat_id
LAST_RESULT_BY_CHAT: Dict[int, List[int]] = {}


def logs(chat_id, operation_type, sort_name: str = "", time_of_sort: str = "", message: str = ""):
    # Время в UTC+3
    now = datetime.utcnow() + timedelta(hours=3)
    # Формат: 11.03.2026.17:57
    timestamp = now.strftime("%d.%m.%Y.%H:%M")

    payload = {
        # Для каждого события генерируем отдельный UUID,
        # как в примере {timestampz:..., chatid:uuid, ...}
        "chatid": str(uuid.uuid4()),
        "timestampz": timestamp,
        "type": operation_type,
        "sort_name": sort_name,
        "time_of_sort": time_of_sort,
        "message": message,
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _format_array(arr: List[int], max_len: int = 50) -> str:
    """Сделать человекочитаемое представление массива для ответа в Telegram."""
    if len(arr) <= max_len:
        return " ".join(map(str, arr))
    return ", ".join(map(str, arr[:max_len])) + f" ... (всего {len(arr)} элементов)"


def _build_sort_keyboard(arr: List[int]) -> types.InlineKeyboardMarkup:
    """Инлайн‑клавиатура с алгоритмами сортировки для заданного массива."""
    kb = types.InlineKeyboardMarkup()
    row: list[types.InlineKeyboardButton] = []
    for key, alg in SORT_KEY_MAP.items():
        # Отключаем counting, bucket и radix, если есть отрицательные числа
        if min(arr) < 0 and alg in (COUNTING, BUCKET, RADIX):
            continue
        # В callback_data кладём только ключ алгоритма, массив храним в памяти по chat_id
        callback_data = f"sort:{key}"
        btn = types.InlineKeyboardButton(text=alg.name, callback_data=callback_data)
        row.append(btn)
        if len(row) == 2:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    return kb


def _register_text_handlers(bot: telebot.TeleBot) -> None:
    @bot.message_handler(commands=["start", "help"])
    def welcome(message: telebot.types.Message) -> None:
        logs(
            message.chat.id,
            "start_help",
            message=f"command={message.text}",
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                text="Написать массив самому", callback_data="start:manual"
            ),
            types.InlineKeyboardButton(
                text="Сгенерировать массив", callback_data="start:gen"
            ),
        )
        bot.reply_to(
            message,
            "Привет! Я бот сортировок.\n"
            "1) Нажми кнопку, чтобы выбрать: написать массив самому или сгенерировать.\n"
            "2) После этого я предложу алгоритмы сортировки кнопками.\n\n"
            "Также доступны команды:\n"
            "• Просто пришли массив чисел (через пробел) — я сразу предложу алгоритмы.\n"
            "• /sort <алгоритм> <числа...> — отсортировать массив командой.\n"
            "  Например: /sort quick 5 3 1 4\n"
            "• /gen — сгенерировать массив по параметрам.\n"
            "• /faq — краткие ответы на частые вопросы.\n\n"
            "Доступные алгоритмы: "
            + ", ".join(SORT_KEY_MAP.keys()),
            reply_markup=kb,
        )

    @bot.message_handler(commands=["faq"])
    def faq(message: telebot.types.Message) -> None:
        logs(message.chat.id, "faq")
        text = (
            "❓ *FAQ по боту сортировок*\n\n"
            "• Я *делаю*: сравниваю разные алгоритмы сортировки на одном массиве и "
            "показываю время работы.\n"
            "• Как начать проще всего: просто пришли массив чисел через пробел, "
            "и я покажу кнопки с доступными алгоритмами.\n"
            "  Например: `5 3 1 4`\n"
            "• Можно использовать команду `/sort <алгоритм> <числа...>`.\n"
            "  Например: `/sort quick 5 3 1 4`\n"
            "• Чтобы сразу сгенерировать массив, используй `/gen` и задай минимум, максимум и количество.\n"
            "• Какие алгоритмы есть: "
            + ", ".join(SORT_KEY_MAP.keys())
            + ".\n"
            "• Для массивов с отрицательными числами алгоритмы `counting`, `bucket` и `radix` "
            "будут недоступны.\n"
            "• При ошибке ввода я попрошу прислать данные ещё раз.\n"
            "• После сортировки я предложу, что делать дальше: отсортировать этот же массив "
            "другим алгоритмом, ввести новый или сгенерировать новый массив.\n\n"
            "Более подробная документация доступна в GitHub‑репозитории:\n"
            "[FAQ.md](https://github.com/ilyaap069-ux/CLI_SORT/blob/master/FAQ.md)."
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["gen"])
    def gen_command(message: telebot.types.Message) -> None:
        logs(message.chat.id, "gen")
        """Войти в режим задания параметров генерации массива."""
        print("")
        GENERATION_AWAITING_PARAMS.add(message.chat.id)
        bot.reply_to(
            message,
            "Введите параметры генерации массива в формате:\n"
            "`минимум максимум количество`\n"
            "Пример: `-10 10 5`",
            parse_mode="Markdown",
        )

    @bot.message_handler(commands=["sort_buttons"])
    def sort_buttons_handler(message: telebot.types.Message) -> None:
        """
        /sort_buttons <числа...>
        Пользователь присылает массив, затем выбирает алгоритм кнопкой.
        """
        parts = message.text.split()
        if len(parts) < 2:
            logs(
                message.chat.id,
                "sort_buttons_error",
                message="no numbers provided",
            )
            bot.reply_to(
                message,
                "Использование: /sort_buttons <числа...>\n"
                "Пример: /sort_buttons 5 3 1 4",
            )
            return

        try:
            arr = [int(x) for x in parts[1:]]
        except ValueError:
            logs(
                message.chat.id,
                "sort_buttons_error",
                message="non‑integer values in array",
            )
            bot.reply_to(
                message,
                "Ошибка: все элементы массива должны быть целыми числами.\n"
                "Пример: /sort_buttons 5 3 1 4",
            )
            return

        if not arr:
            logs(
                message.chat.id,
                "sort_buttons_error",
                message="empty array",
            )
            bot.reply_to(
                message,
                "Массив не может быть пустым. Укажите хотя бы одно число.",
            )
            return

        LAST_ARRAY_BY_CHAT[message.chat.id] = arr
        bot.reply_to(
            message,
            "Выберите алгоритм сортировки для этого массива:",
            reply_markup=_build_sort_keyboard(arr),
        )
        logs(
            message.chat.id,
            "sort_buttons",
            message=f"len={len(arr)}",
        )

    @bot.message_handler(func=lambda m: not m.text.startswith("/"))
    def array_message_handler(message: telebot.types.Message) -> None:
        """Пользователь прислал массив или параметры генерации."""
        chat_id = message.chat.id

        # Сначала обрабатываем режим "ждём параметры генерации"
        if chat_id in GENERATION_AWAITING_PARAMS:
            parts = message.text.split()
            logs(chat_id, "gen_params")
            if len(parts) != 3:
                bot.reply_to(
                    message,
                    "Ожидаю три целых числа: минимум, максимум и количество.\n"
                    "Пример: `-10 10 5`",
                    parse_mode="Markdown",
                )
                return
            try:
                minim, maxim, count = map(int, parts)
            except ValueError:
                logs(
                    chat_id,
                    "gen_params_error",
                    message="non‑integer generator params",
                )
                bot.reply_to(
                    message,
                    "Все три параметра должны быть целыми числами.\n"
                    "Пример: `-10 10 5`",
                    parse_mode="Markdown",
                )
                return

            if count <= 0:
                logs(
                    chat_id,
                    "gen_params_error",
                    message=f"non‑positive count={count}",
                )
                bot.reply_to(
                    message,
                    "Количество элементов должно быть > 0.",
                )
                return

            if minim > maxim:
                logs(
                    chat_id,
                    "gen_params_error",
                    message=f"min>{'{'}max{'}'}: {minim}>{maxim}",
                )
                bot.reply_to(
                    message,
                    "Минимум не может быть больше максимума. Попробуйте ещё раз.\n"
                    "Пример: `-10 10 5`",
                    parse_mode="Markdown",
                )
                return

            arr = [randint(minim, maxim) for _ in range(count)]
            GENERATION_AWAITING_PARAMS.discard(chat_id)
            LAST_ARRAY_BY_CHAT[chat_id] = arr
            logs(
                chat_id,
                "gen_params_ok",
                message=f"min={minim}, max={maxim}, count={count}",
            )

            kb = _build_sort_keyboard(arr)
            bot.reply_to(
                message,
                "Сгенерированный массив:\n"
                f"`{_format_array(arr)}`\n"
                "Выберите алгоритм сортировки:",
                parse_mode="Markdown",
                reply_markup=kb,
            )
            return

        # Обычный режим — пользователь прислал готовый массив
        parts = message.text.split()
        logs(chat_id, "array_message")
        try:
            arr = [int(x) for x in parts]
        except ValueError:
            logs(
                chat_id,
                "array_message_error",
                message="non‑integer values in array",
            )
            bot.reply_to(
                message,
                "Я ожидаю массив целых чисел, разделённых пробелами.\n"
                "Пример: `5 3 1 4`",
                parse_mode="Markdown",
            )
            return

        if not arr:
            logs(
                chat_id,
                "array_message_error",
                message="empty array",
            )
            bot.reply_to(
                message,
                "Массив не может быть пустым. Укажите хотя бы одно число.",
            )
            return

        LAST_ARRAY_BY_CHAT[chat_id] = arr
        kb = _build_sort_keyboard(arr)
        bot.reply_to(
            message,
            "Выберите алгоритм сортировки для этого массива:",
            reply_markup=kb,
        )

    @bot.message_handler(commands=["sort"])
    def sort_handler(message: telebot.types.Message) -> None:
        """
        /sort <алгоритм> <числа...>
        Например: /sort quick 5 3 1 4
        """
        parts = message.text.split()
        # Если пользователь ввёл только "/sort" без параметров —
        # ведём себя так же, как при нажатии кнопки
        # "Написать массив самому".
        if len(parts) == 1:
            logs(
                message.chat.id,
                "start_manual",
                message="user used /sort without arguments",
            )
            bot.reply_to(
                message,
                "Напишите массив целых чисел через пробел.\n"
                "Пример: `5 3 1 4`",
                parse_mode="Markdown",
            )
            return

        if len(parts) < 3:
            logs(
                message.chat.id,
                "sort_error",
                message="not enough arguments",
            )
            bot.reply_to(
                message,
                "Использование: /sort <алгоритм> <числа...>\n"
                "Например: /sort quick 5 3 1 4\n"
                "Доступные алгоритмы: " + ", ".join(SORT_KEY_MAP.keys()),
            )
            return

        algo_key = parts[1].lower()
        if algo_key not in SORT_KEY_MAP:
            logs(
                message.chat.id,
                "sort_error",
                message=f"unknown algorithm={algo_key}",
            )
            bot.reply_to(
                message,
                "Неизвестный алгоритм сортировки.\n"
                "Доступные алгоритмы: " + ", ".join(SORT_KEY_MAP.keys()),
            )
            return

        try:
            arr = [int(x) for x in parts[2:]]
        except ValueError:
            logs(
                message.chat.id,
                "sort_error",
                message="non‑integer values in array",
            )
            bot.reply_to(
                message,
                "Ошибка: все элементы массива должны быть целыми числами.\n"
                "Пример: /sort quick 5 3 1 4",
            )
            return

        if not arr:
            logs(
                message.chat.id,
                "sort_error",
                message="empty array",
            )
            bot.reply_to(
                message,
                "Массив не может быть пустым. Укажите хотя бы одно число.",
            )
            return

        sort_alg = SORT_KEY_MAP[algo_key]

        # Ограничение для counting, bucket и radix при отрицательных числах
        if min(arr) < 0 and sort_alg in (COUNTING, BUCKET, RADIX):
            logs(
                message.chat.id,
                "sort_error",
                sort_name=algo_key,
                message="negative numbers not allowed for counting/bucket/radix",
            )
            bot.reply_to(
                message,
                "Алгоритмы counting, bucket и radix не работают с отрицательными числами.\n"
                "Выберите другой алгоритм или используйте массив только из неотрицательных чисел.",
            )
            return
        try:
            d1, d2, res = sort_result(sort_alg, arr)
            logs(
                message.chat.id,
                "sort",
                sort_name=algo_key,
                time_of_sort=d1,
            )
        except ValueError as e:
            logs(
                message.chat.id,
                "sort_exception",
                sort_name=algo_key,
                message=f"ValueError: {e}",
            )
            bot.reply_to(message, f"Ошибка при сортировке: {e}")
            return
        except Exception:
            logs(
                message.chat.id,
                "sort_exception",
                sort_name=algo_key,
                message="unexpected error during sort",
            )
            bot.reply_to(
                message,
                "Произошла внутренняя ошибка при сортировке. "
                "Попробуйте другой массив или алгоритм.",
            )
            return

        LAST_RESULT_BY_CHAT[message.chat.id] = res

        formatted_arr = _format_array(res)
        reply_text = (
            f"*Алгоритм*: `{sort_alg.name}`\n"
            f"*Время алгоритма*: `{d1} мс`\n"
            f"*Время встроенной сортировки*: `{d2} мс`\n"
            f"*Отсортированный массив*:\n`{formatted_arr}`"
        )

        # Кнопки: показать весь массив (если он длинный) и показать код алгоритма
        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                text="Показать код алгоритма", callback_data=f"code:{algo_key}"
            )
        )
        if len(res) > 50:
            kb.row(
                types.InlineKeyboardButton(
                    text="Показать весь массив", callback_data="show:full"
                )
            )
        bot.reply_to(message, reply_text, parse_mode="Markdown", reply_markup=kb)


def _register_callback_handlers(bot: telebot.TeleBot) -> None:
    @bot.callback_query_handler(func=lambda call: call.data.startswith("start:"))
    def handle_start_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, action = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if action == "manual":
            logs(
                call.message.chat.id,
                "start_manual",
                message="user chose manual array input",
            )
            bot.send_message(
                call.message.chat.id,
                "Напишите массив целых чисел через пробел.\n"
                "Пример: `5 3 1 4`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        if action == "gen":
            logs(
                call.message.chat.id,
                "start_gen",
                message="user chose generator params",
            )
            GENERATION_AWAITING_PARAMS.add(call.message.chat.id)
            bot.send_message(
                call.message.chat.id,
                "Введите параметры генерации массива в формате:\n"
                "`минимум максимум количество`\n"
                "Пример: `-10 10 5`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("sort:"))
    def handle_sort_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, algo_key = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id, "Некорректные данные для сортировки.")
            return

        if algo_key not in SORT_KEY_MAP:
            logs(
                call.message.chat.id,
                "sort_callback_error",
                message=f"unknown algorithm={algo_key}",
            )
            bot.answer_callback_query(call.id, "Неизвестный алгоритм.")
            return

        chat_id = call.message.chat.id
        arr = LAST_ARRAY_BY_CHAT.get(chat_id)
        if not arr:
            logs(
                chat_id,
                "sort_callback_error",
                message="array not found for chat",
            )
            bot.answer_callback_query(call.id, "Массив не найден. Пришлите его ещё раз.")
            return

        sort_alg = SORT_KEY_MAP[algo_key]

        # Ограничение для counting, bucket и radix при отрицательных числах
        if min(arr) < 0 and sort_alg in (COUNTING, BUCKET, RADIX):
            logs(
                chat_id,
                "sort_callback_error",
                sort_name=algo_key,
                message="negative numbers not allowed for counting/bucket/radix",
            )
            bot.answer_callback_query(
                call.id,
                "counting, bucket и radix не работают с отрицательными числами.",
                show_alert=True,
            )
            return

        try:
            d1, d2, res = sort_result(sort_alg, arr)
            logs(
                chat_id,
                "sort_callback",
                sort_name=algo_key,
                time_of_sort=d1,
            )
        except ValueError as e:
            logs(
                chat_id,
                "sort_callback_exception",
                sort_name=algo_key,
                message=f"ValueError: {e}",
            )
            bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)
            return
        except Exception:
            logs(
                chat_id,
                "sort_callback_exception",
                sort_name=algo_key,
                message="unexpected error during sort",
            )
            bot.answer_callback_query(
                call.id,
                "Внутренняя ошибка при сортировке.",
                show_alert=True,
            )
            return

        LAST_RESULT_BY_CHAT[chat_id] = res
        formatted_arr = _format_array(res)
        # Оборачиваем сложности в обратные кавычки, чтобы символы `*` и `(` `)`
        # не ломали Markdown‑разметку.
        reply_text = (
            f"*Алгоритм*: `{sort_alg.name}`\n"
            f"*Time complexity*: `{sort_alg.time_complexity}`\n"
            f"*Space complexity*: `{sort_alg.space_complexity}`\n"
            f"*Время алгоритма*: `{d1} мс`\n"
            f"*Время встроенной сортировки*: `{d2} мс`\n"
            f"*Отсортированный массив*:\n`{formatted_arr}`"
        )

        # Кнопки управления результатом сортировки
        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                text="Показать код алгоритма", callback_data=f"code:{algo_key}"
            )
        )
        if len(res) > 50:
            kb.row(
                types.InlineKeyboardButton(
                    text="Показать весь массив", callback_data="show:full"
                )
            )
        try:
            bot.send_message(chat_id, reply_text, parse_mode="Markdown", reply_markup=kb)
        except ApiTelegramException as e:
            logs(
                chat_id,
                "telegram_send_error",
                sort_name=algo_key,
                message=str(e),
            )
            return

        # Кнопки "что делать дальше"
        next_kb = types.InlineKeyboardMarkup()
        next_kb.row(
            types.InlineKeyboardButton(
                text="Выбрать другой алгоритм для этого массива",
                callback_data="next:again",
            )
        )
        next_kb.row(
            types.InlineKeyboardButton(
                text="Ввести новый массив", callback_data="next:new"
            ),
            types.InlineKeyboardButton(
                text="Сгенерировать массив", callback_data="next:gen"
            ),
        )
        bot.send_message(
            call.message.chat.id,
            "Что делать дальше?",
            reply_markup=next_kb,
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("next:"))
    def handle_next_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, action = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        chat_id = call.message.chat.id

        if action == "again":
            logs(
                chat_id,
                "next_again",
                message="user wants another algorithm for same array",
            )
            arr = LAST_ARRAY_BY_CHAT.get(chat_id)
            if not arr:
                bot.answer_callback_query(call.id, "Массив не найден. Пришлите его ещё раз.")
                return
            kb = _build_sort_keyboard(arr)
            bot.send_message(
                chat_id,
                "Выберите алгоритм сортировки для этого массива:",
                reply_markup=kb,
            )
            bot.answer_callback_query(call.id)
            return

        if action == "new":
            logs(
                chat_id,
                "next_new",
                message="user wants to enter new array",
            )
            bot.send_message(
                chat_id,
                "Пришлите новый массив чисел через пробел.\n"
                "Пример: `10 3 -2 5`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        if action == "gen":
            logs(
                chat_id,
                "next_gen",
                message="user wants to generate new array",
            )
            # Переходим в режим запроса параметров генерации
            GENERATION_AWAITING_PARAMS.add(chat_id)
            bot.send_message(
                chat_id,
                "Введите параметры генерации массива в формате:\n"
                "`минимум максимум количество`\n"
                "Пример: `-10 10 5`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("show:"))
    def handle_show_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, action = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if action != "full":
            bot.answer_callback_query(call.id)
            return

        chat_id = call.message.chat.id
        logs(
            chat_id,
            "show_full",
            message="user requested full sorted array",
        )
        arr = LAST_RESULT_BY_CHAT.get(chat_id)
        if not arr:
            bot.answer_callback_query(call.id, "Массив не найден. Отсортируйте его ещё раз.")
            return

        # Отправляем весь массив кусками, чтобы не превысить лимит Telegram
        text = " ".join(map(str, arr))
        chunk_size = 3500
        for i in range(0, len(text), chunk_size):
            bot.send_message(chat_id, text[i : i + chunk_size])

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("code:"))
    def handle_code_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, algo_key = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if algo_key not in SORT_KEY_MAP:
            logs(
                call.message.chat.id,
                "code_callback_error",
                message=f"unknown algorithm={algo_key}",
            )
            bot.answer_callback_query(call.id, "Неизвестный алгоритм.")
            return

        sort_alg = SORT_KEY_MAP[algo_key]

        # Собираем код основной функции и, при необходимости, вспомогательных
        sources: list[str] = []
        try:
            sources.append(inspect.getsource(sort_alg.sort_function))
        except OSError:
            bot.answer_callback_query(call.id, "Не удалось получить код алгоритма.")
            return

        # Для merge sort добавляем функцию merge, для heap sort — heapify.
        if algo_key == "merge":
            try:
                sources.append(inspect.getsource(sort_func.merge))
            except OSError:
                pass
        elif algo_key == "heap":
            try:
                sources.append(inspect.getsource(sort_func.heapify))
            except OSError:
                pass

        full_source = "\n\n".join(sources)

        # Текстовое описание алгоритма (если есть)
        description = ALGO_DESCRIPTIONS.get(algo_key, "")

        # Логируем просмотр кода и описания алгоритма
        logs(
            call.message.chat.id,
            "code_view",
            sort_name=algo_key,
            message=description,
        )
        if description:
            header = (
                f"*Алгоритм* `{sort_alg.name}`\n"
                f"{description}\n\n"
                f"*Код алгоритма:*\n"
            )
        else:
            header = f"*Код алгоритма* `{sort_alg.name}`:\n"

        # Отправляем описание и код отдельным сообщением в формате Markdown
        code_text = f"{header}```python\n{full_source}\n```"
        bot.send_message(call.message.chat.id, code_text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)


def register_handlers(bot: telebot.TeleBot) -> None:
    """Подключить все обработчики к переданному боту."""
    _register_text_handlers(bot)
    _register_callback_handlers(bot)

