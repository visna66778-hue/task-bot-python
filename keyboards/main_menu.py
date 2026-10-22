from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Кнопки главного меню бота
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/add"),
            KeyboardButton(text="/list"),
        ],
        [
            KeyboardButton(text="/list_csv"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие",
)