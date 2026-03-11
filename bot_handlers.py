from random import randint
from typing import Dict, List, Set

import telebot
from telebot import types

from sort_config import sort_result
from sorts import ARRAY_OF_SORTS, BUCKET, COUNTING


# Короткие ключи для алгоритмов сортировки, например: /sort quick 3 1 2
SORT_KEY_MAP = {alg.name.split()[0].lower(): alg for alg in ARRAY_OF_SORTS}

# Чаты, для которых мы ждём параметры генерации (min max count)
GENERATION_AWAITING_PARAMS: Set[int] = set()

# Последний исходный массив пользователя (по chat_id)
LAST_ARRAY_BY_CHAT: Dict[int, List[int]] = {}

# Последний отсортированный массив (результат) по chat_id
LAST_RESULT_BY_CHAT: Dict[int, List[int]] = {}


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
        # Отключаем counting и bucket, если есть отрицательные числа
        if min(arr) < 0 and alg in (COUNTING, BUCKET):
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
            "• Для массивов с отрицательными числами алгоритмы `counting` и `bucket` "
            "будут недоступны.\n"
            "• При ошибке ввода я попрошу прислать данные ещё раз.\n"
            "• После сортировки я предложу, что делать дальше: отсортировать этот же массив "
            "другим алгоритмом, ввести новый или сгенерировать новый массив.\n\n"
            "Более подробная документация доступна в файле FAQ.md проекта."
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    @bot.message_handler(commands=["gen"])
    def gen_command(message: telebot.types.Message) -> None:
        """Войти в режим задания параметров генерации массива."""
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
            bot.reply_to(
                message,
                "Использование: /sort_buttons <числа...>\n"
                "Пример: /sort_buttons 5 3 1 4",
            )
            return

        try:
            arr = [int(x) for x in parts[1:]]
        except ValueError:
            bot.reply_to(
                message,
                "Ошибка: все элементы массива должны быть целыми числами.\n"
                "Пример: /sort_buttons 5 3 1 4",
            )
            return

        if not arr:
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

    @bot.message_handler(func=lambda m: not m.text.startswith("/"))
    def array_message_handler(message: telebot.types.Message) -> None:
        """Пользователь прислал массив или параметры генерации."""
        chat_id = message.chat.id

        # Сначала обрабатываем режим "ждём параметры генерации"
        if chat_id in GENERATION_AWAITING_PARAMS:
            parts = message.text.split()
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
                bot.reply_to(
                    message,
                    "Все три параметра должны быть целыми числами.\n"
                    "Пример: `-10 10 5`",
                    parse_mode="Markdown",
                )
                return

            if count <= 0:
                bot.reply_to(
                    message,
                    "Количество элементов должно быть > 0.",
                )
                return

            if minim > maxim:
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
        try:
            arr = [int(x) for x in parts]
        except ValueError:
            bot.reply_to(
                message,
                "Я ожидаю массив целых чисел, разделённых пробелами.\n"
                "Пример: `5 3 1 4`",
                parse_mode="Markdown",
            )
            return

        if not arr:
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
        if len(parts) < 3:
            bot.reply_to(
                message,
                "Использование: /sort <алгоритм> <числа...>\n"
                "Например: /sort quick 5 3 1 4\n"
                "Доступные алгоритмы: " + ", ".join(SORT_KEY_MAP.keys()),
            )
            return

        algo_key = parts[1].lower()
        if algo_key not in SORT_KEY_MAP:
            bot.reply_to(
                message,
                "Неизвестный алгоритм сортировки.\n"
                "Доступные алгоритмы: " + ", ".join(SORT_KEY_MAP.keys()),
            )
            return

        try:
            arr = [int(x) for x in parts[2:]]
        except ValueError:
            bot.reply_to(
                message,
                "Ошибка: все элементы массива должны быть целыми числами.\n"
                "Пример: /sort quick 5 3 1 4",
            )
            return

        if not arr:
            bot.reply_to(
                message,
                "Массив не может быть пустым. Укажите хотя бы одно число.",
            )
            return

        sort_alg = SORT_KEY_MAP[algo_key]

        # Ограничение для counting и bucket при отрицательных числах
        if min(arr) < 0 and sort_alg in (COUNTING, BUCKET):
            bot.reply_to(
                message,
                "Алгоритмы counting и bucket не работают с отрицательными числами.\n"
                "Выберите другой алгоритм или используйте массив только из неотрицательных чисел.",
            )
            return

        try:
            d1, d2, res = sort_result(sort_alg, arr)
        except ValueError as e:
            bot.reply_to(message, f"Ошибка при сортировке: {e}")
            return
        except Exception:
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
        # Если массив усечён, добавляем кнопку "Показать весь массив"
        if len(res) > 50:
            kb = types.InlineKeyboardMarkup()
            kb.row(
                types.InlineKeyboardButton(
                    text="Показать весь массив", callback_data="show:full"
                )
            )
            bot.reply_to(message, reply_text, parse_mode="Markdown", reply_markup=kb)
        else:
            bot.reply_to(message, reply_text, parse_mode="Markdown")


def _register_callback_handlers(bot: telebot.TeleBot) -> None:
    @bot.callback_query_handler(func=lambda call: call.data.startswith("start:"))
    def handle_start_callback(call: telebot.types.CallbackQuery) -> None:
        try:
            _, action = call.data.split(":", maxsplit=1)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if action == "manual":
            bot.send_message(
                call.message.chat.id,
                "Напишите массив целых чисел через пробел.\n"
                "Пример: `5 3 1 4`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        if action == "gen":
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
            bot.answer_callback_query(call.id, "Неизвестный алгоритм.")
            return

        chat_id = call.message.chat.id
        arr = LAST_ARRAY_BY_CHAT.get(chat_id)
        if not arr:
            bot.answer_callback_query(call.id, "Массив не найден. Пришлите его ещё раз.")
            return

        sort_alg = SORT_KEY_MAP[algo_key]

        # Ограничение для counting и bucket при отрицательных числах
        if min(arr) < 0 and sort_alg in (COUNTING, BUCKET):
            bot.answer_callback_query(
                call.id,
                "counting и bucket не работают с отрицательными числами.",
                show_alert=True,
            )
            return

        try:
            d1, d2, res = sort_result(sort_alg, arr)
        except ValueError as e:
            bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)
            return
        except Exception:
            bot.answer_callback_query(
                call.id,
                "Внутренняя ошибка при сортировке.",
                show_alert=True,
            )
            return

        LAST_RESULT_BY_CHAT[chat_id] = res

        formatted_arr = _format_array(res)
        reply_text = (
            f"*Алгоритм*: `{sort_alg.name}`\n"
            f"*Время алгоритма*: `{d1} мс`\n"
            f"*Время встроенной сортировки*: `{d2} мс`\n"
            f"*Отсортированный массив*:\n`{formatted_arr}`"
        )
        if len(res) > 50:
            kb = types.InlineKeyboardMarkup()
            kb.row(
                types.InlineKeyboardButton(
                    text="Показать весь массив", callback_data="show:full"
                )
            )
            bot.send_message(chat_id, reply_text, parse_mode="Markdown", reply_markup=kb)
        else:
            bot.send_message(chat_id, reply_text, parse_mode="Markdown")

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
            bot.send_message(
                chat_id,
                "Пришлите новый массив чисел через пробел.\n"
                "Пример: `10 3 -2 5`",
                parse_mode="Markdown",
            )
            bot.answer_callback_query(call.id)
            return

        if action == "gen":
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


def register_handlers(bot: telebot.TeleBot) -> None:
    """Подключить все обработчики к переданному боту."""
    _register_text_handlers(bot)
    _register_callback_handlers(bot)

