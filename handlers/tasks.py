from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, BufferedInputFile

from database.db import add_task, get_all_tasks, update_task_status
from keyboards.main_menu import main_keyboard
from services.csv_export import tasks_to_csv

router = Router()


class TaskForm(StatesGroup):
    waiting_for_text = State()
    waiting_for_category = State()


def get_author(message: Message) -> str:
    """Определяет автора задачи."""
    if message.from_user.username:
        return f"@{message.from_user.username}"
    return message.from_user.full_name


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для общего списка задач.\n\n"
        "/add — добавить задачу\n"
        "/list — посмотреть все задачи\n"
        "/list_csv — скачать задачи в CSV\n"
        "/cancel — отменить добавление",
        reply_markup=main_keyboard,
    )


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(TaskForm.waiting_for_text)
    await message.answer("Напиши текст новой задачи.")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добавление задачи отменено.")


@router.message(Command("list"))
async def cmd_list(message: Message):
    tasks = get_all_tasks()

    if not tasks:
        await message.answer("Список задач пока пуст.")
        return

    lines = []

    for task in tasks:
        lines.append(
            f"#{task['id']} — {task['text']}\n"
            f"Категория: {task['category']}\n"
            f"Статус: {task['status']}\n"
            f"Автор: {task['user']}\n"
            f"Создана: {task['created_at']}"
        )

    chunk = ""

    for line in lines:
        candidate = f"{chunk}\n\n{line}" if chunk else line

        if len(candidate) > 3500:
            await message.answer(chunk)
            chunk = line
        else:
            chunk = candidate

    if chunk:
        await message.answer(chunk)

        
@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer(
        "Чтобы изменить статус задачи, отправь сообщение в формате:\n\n"
        "/setstatus 1 В работе\n\n"
        "Вместо 1 укажи номер задачи.\n"
        "Доступные статусы: Новая, В работе, Выполнена."
    )


@router.message(Command("setstatus"))
async def cmd_set_status(message: Message):
    if not message.text:
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:
        await message.answer(
            "Неверный формат.\n"
            "Пример: /setstatus 1 Выполнена"
        )
        return

    try:
        task_id = int(parts[1])
    except ValueError:
        await message.answer("Номер задачи должен быть числом.")
        return

    if task_id <= 0:
        await message.answer("Номер задачи должен быть положительным.")
        return

    status = parts[2].strip()
    allowed_statuses = {
        "новая": "Новая",
        "в работе": "В работе",
        "выполнена": "Выполнена",
    }

    normalized_status = allowed_statuses.get(status.casefold())

    if normalized_status is None:
        await message.answer(
            "Неизвестный статус.\n"
            "Выбери один из вариантов: Новая, В работе, Выполнена."
        )
        return

    updated = update_task_status(task_id, normalized_status)

    if updated:
        await message.answer(
            f"Статус задачи №{task_id} изменён на «{normalized_status}»."
        )
    else:
        await message.answer(f"Задача №{task_id} не найдена.")



@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message):
    tasks = get_all_tasks()

    if not tasks:
        await message.answer("Список задач пока пуст.")
        return

    csv_data = tasks_to_csv(tasks)
    file = BufferedInputFile(csv_data, filename="tasks.csv")

    await message.answer_document(
        document=file,
        caption=f"Общий список задач: {len(tasks)} шт.",
    )


@router.message(TaskForm.waiting_for_text)
async def receive_task_text(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправь текст задачи.")
        return

    text = message.text.strip()

    if text == "/cancel":
        await state.clear()
        await message.answer("Добавление отменено.")
        return

    if text.startswith("/"):
        await message.answer("Отправь текст задачи или /cancel.")
        return

    if not text:
        await message.answer("Текст задачи не может быть пустым.")
        return

    await state.update_data(task_text=text)
    await state.set_state(TaskForm.waiting_for_category)

    await message.answer(
        "Укажи категорию задачи, например:\n"
        "Работа, Учёба, Личное.\n\n"
        "Или отправь /skip, чтобы выбрать категорию «Общее»."
    )


@router.message(TaskForm.waiting_for_category)
async def receive_task_category(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Напиши категорию или отправь /skip.")
        return

    category = message.text.strip()

    if category == "/cancel":
        await state.clear()
        await message.answer("Добавление отменено.")
        return

    if category.startswith("/") and category != "/skip":
        await message.answer("Укажи категорию, /skip или /cancel.")
        return

    if category == "/skip":
        category = "Общее"

    if len(category) > 50:
        await message.answer("Категория должна быть не длиннее 50 символов.")
        return

    data = await state.get_data()
    task_text = data["task_text"]

    add_task(
        text=task_text,
        username=get_author(message),
        category=category,
        status="Новая",
    )

    await state.clear()

    await message.answer(
        f"Задача добавлена!\n\n"
        f"Задача: {task_text}\n"
        f"Категория: {category}\n"
        f"Статус: Новая",
        reply_markup=main_keyboard,
    )