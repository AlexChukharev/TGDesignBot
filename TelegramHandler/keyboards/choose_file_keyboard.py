from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def choose_file_kb_query_handler(key_list: list, can_go_left: bool, can_go_right: bool) -> list:
    nums_for_choose = [
        InlineKeyboardButton(
            text=str(x),
            callback_data=str(x)
        ) for x in range(1, key_list.__len__() + 1)
    ]
    rows = [
        nums_for_choose,
    ]
    if (can_go_left and can_go_right):
        rows.append([
            InlineKeyboardButton(
                text='⬅Назад',
                callback_data='prev'
            ),
            InlineKeyboardButton(
                text='Далее➡',
                callback_data='next'
            )
        ])

    elif (can_go_right):
        rows.append([
            InlineKeyboardButton(
                text='Далее➡',
                callback_data='next'
            )
        ])
    elif (can_go_left):
        rows.append([
            InlineKeyboardButton(
                text='⬅Назад',
                callback_data='prev'
            )
        ])
    return rows


async def choose_file_kb_query(key_list: list, can_go_left: bool, can_go_right: bool) -> InlineKeyboardMarkup:
    rows = await choose_file_kb_query_handler(key_list, can_go_left, can_go_right)
    rows.append([
        InlineKeyboardButton(
            text='В главное меню',
            # callback_data='menu_choose'
            callback_data='start'
        )
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def download_file_query() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text='Получить шрифты',
                callback_data='get_fonts'
            )
        ],
        [
            InlineKeyboardButton(
                text='В главное меню',
                # callback_data='menu_choose'
                callback_data='start'
            )
        ]

    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def work_with_tags_query(key_list: list, can_go_left: bool,
                               can_go_right: bool, state: FSMContext) -> InlineKeyboardMarkup:
    user_info = await state.get_data()
    user_tags = user_info['user_tags']
    nums_for_choose = [
        InlineKeyboardButton(
            text=str(x),
            callback_data=str(x)
        ) for x in range(1, key_list.__len__() + 1)
    ]
    rows = [
        nums_for_choose,
    ]
    if (can_go_left and can_go_right):
        rows.append([
            InlineKeyboardButton(
                text='⬅Назад',
                callback_data='prev'
            ),
            InlineKeyboardButton(
                text='Далее➡',
                callback_data='next'
            )
        ])

    elif can_go_right:
        rows.append([
            InlineKeyboardButton(
                text='Далее➡',
                callback_data='next'
            )
        ])
    elif can_go_left:
        rows.append([
            InlineKeyboardButton(
                text='⬅Назад',
                callback_data='prev'
            )
        ])
    if len(user_tags) > 0:
        rows.append([
            InlineKeyboardButton(
                text="Очистить теги",
                callback_data='clear_tags'
            )
        ])
    rows.append([
        InlineKeyboardButton(
            text="Найти слайды по введеным тегам",
            callback_data='find_with_tags'
        )
    ])
    rows.append([
        InlineKeyboardButton(
            text='Вернуться к выбору материалов',
            callback_data='menu_choose'
        )
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
