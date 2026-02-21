"""Menu and state machine."""
from enum import Enum
from sorts import ARRAY_OF_SORTS, BUCKET, COUNTING
from sort_config import (array_generator, run_sort)


class State(Enum):
    GREETING = "greeting"
    CHOOSE_SOURCE = "choose_source"
    ENTER_ARRAY = "enter_array"
    GENERATE_ARRAY = "generate_array"
    PICK_SORT = "pick_sort"
    CHOOSE_NEXT = "choose_next"
    EXIT = "exit"


def greetings():
    print("Привет Пользователь! \nЭто программа, для сравнения сортировок")


def exit():  # noqa: A001
    print("Спасибо за использование!")


def start():
    """manual or generate. Returns 0, 1 or None on invalid."""
    try:
        gen = int(
            input(
                "Вы хотите написать массив или сгенерировать? \n"
                "0.Написать массив \n1.Сгенерировать \nВведите здесь >>> "
            )
        )
        if gen in (0, 1):
            return gen
    except ValueError:
        pass
    return None


def errormessage(msg: str):
    print(f"Ошибка: {msg}")


class Menu:
    def __init__(self):
        self.state = State.GREETING
        self.arr: list[int] | None = None
        self.sorts_for_arr: list

    def _sorts_for_arr(self):
        if not self.arr:
            return ARRAY_OF_SORTS
        if min(self.arr) >= 0:
            return ARRAY_OF_SORTS
        return [s for s in ARRAY_OF_SORTS if s not in (COUNTING, BUCKET)]

    def run(self):
        while self.state != State.EXIT:
            try:
                self._step()
            except Exception:
                errormessage("Произошла непредвиденная ошибка. Попробуйте ещё раз.")
                if self.state == State.CHOOSE_SOURCE:
                    self.state = State.CHOOSE_SOURCE
                elif self.state in (State.PICK_SORT, State.CHOOSE_NEXT):
                    self.state = State.CHOOSE_NEXT
        exit()

    def _step(self):
        if self.state == State.GREETING:
            greetings()
            self.state = State.CHOOSE_SOURCE

        elif self.state == State.CHOOSE_SOURCE:
            choice = start()
            if choice is None:
                errormessage("введите 0 или 1.")
                return
            if choice == 0:
                self.state = State.ENTER_ARRAY
            else:
                self.state = State.GENERATE_ARRAY

        elif self.state == State.ENTER_ARRAY:
            try:
                self.arr = list(
                    map(
                        int,
                        input("Введите ваш массив без скобок, через пробел >>> ").split(),
                    )
                )
            except ValueError:
                errormessage("введите числа через пробел, без скобок.")
                return
            if not self.arr:
                errormessage("массив не может быть пустым.")
                return
            self.sorts_for_arr = self._sorts_for_arr()
            self.state = State.PICK_SORT

        elif self.state == State.GENERATE_ARRAY:
            self.arr = array_generator()
            if self.arr is None:
                errormessage("введите целые числа.")
                self.state = State.CHOOSE_SOURCE
                return
            if not self.arr:
                errormessage("массив не может быть пустым. Введите количество > 0.")
                self.state = State.CHOOSE_SOURCE
                return
            self.sorts_for_arr = self._sorts_for_arr()
            self.state = State.PICK_SORT

        elif self.state == State.PICK_SORT:
            ok, msg = run_sort(self.sorts_for_arr, self.arr)
            if not ok:
                errormessage(msg)
                return
            self.state = State.CHOOSE_NEXT

        elif self.state == State.CHOOSE_NEXT:
            print("Что делать дальше?")
            try:
                a = int(
                    input(
                        "0.Отсортировать этот же массив \n"
                        "1.Ввести другой массив \n"
                        "2.Выйти из программы \nВведите номер: "
                    )
                )
            except ValueError:
                errormessage("введите число 0, 1 или 2.")
                return
            if a == 0:
                self.state = State.PICK_SORT
            elif a == 1:
                self.state = State.CHOOSE_SOURCE
            elif a == 2:
                self.state = State.EXIT
            else:
                errormessage("Нет такого номера. Введите 0, 1 или 2.")
