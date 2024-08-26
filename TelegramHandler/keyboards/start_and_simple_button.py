from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from utility.checkers import is_admin


# Starting menu.
def start_menu_kb(message: Message) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Поиск материалов")

    # kb.button(text="Стоп, а что ты умеешь?")
    kb.button(text="Хочу дать обратную связь")
    kb.adjust(1)
    if is_admin(message.from_user.id):
        kb.button(text="Админ-панель")
    return kb.as_markup(resize_keyboard=True)


def start_menu_kb_query(callback_query: CallbackQuery) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Поиск материалов")

    # kb.button(text="Стоп, а что ты умеешь?")
    kb.button(text="Хочу дать обратную связь")
    kb.adjust(1)
    if is_admin(callback_query.from_user.id):
        kb.button(text="Админ-панель")
    return kb.as_markup(resize_keyboard=True)


def only_main_menu_button_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="В главное меню")
    return kb.as_markup(resize_keyboard=True)


def main_menu_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Как установить шрифты?")
    kb.button(text="В главное меню")
    return kb.as_markup(resize_keyboard=True)


def main_menu_kb_query():
    rows = [
        [
            InlineKeyboardButton(
                text='Как установить шрифты?',
                callback_data='install_fonts_help'
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться к выбору материалов',
                callback_data='menu_choose'
            )
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


# Buttons with choosing categories.
# def choose_category_kb() -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="Шаблон презентаций")
#     kb.button(text="Готовые слайды о компании")
#     kb.button(text="Корпоративные шрифты")
#     kb.button(text="В главное меню")
#     kb.adjust(1)
#     return kb.as_markup(resize_keyboard=True)


async def choose_category_text(key_list: list) -> str:
    print(key_list)
    text = "Выберите одну из папок, или выведите все вложенные в эти папки файлы \n \n"

    counter = 1
    for key in key_list:
        text += f"{counter}. {key} \n \n"
        counter += 1
    return text

async def choose_template_text_inner(folder: str, key_list: list) -> str:
    print(key_list)
    text = f"У нас есть несколько шаблонов для подразделения {folder}\nКакой тебе нужен?\n \n"

    # counter = 1
    # for key in key_list:
    #     text += f"{counter}. {key} \n \n"
    #     counter += 1
    return text


async def choose_template_text_root(key_list: list) -> str:
    print(key_list)
    text = f"Для какого подразделения шаблон?\n"

    # counter = 1
    # for key in key_list:
    #     text += f"{counter}. {key} \n \n"
    #     counter += 1
    return text


async def choose_one_file(key_list: list, paths_list: list) -> str:
    text = "Выберите один из файлов для установки \n \n"
    text += await key_list_with_paths(key_list, paths_list)
    return text


async def key_list_to_text(key_list: list) -> str:
    text = ""
    counter = 1
    for key in key_list:
        text += f"{counter}. {key} \n \n"
        counter += 1
    return text


async def key_list_with_paths(key_list: list, path_list: list) -> str:
    text = ""
    counter = 1
    for elem_num in range(len(key_list)):
        text += f"{counter}. {key_list[elem_num]} \n"
        text += f"Путь: {path_list[elem_num]} \n \n"
        counter += 1
    return text


async def choose_tags_query(key_list: list) -> str:
    print(key_list)
    text = ""

    counter = 1
    for key in key_list:
        text += f"{counter}. {key} \n \n"
        counter += 1
    return text


async def choose_category_callback(key_list: list, can_go_left: bool, can_go_right: bool,
                                   can_go_back: bool, file_type: str) -> InlineKeyboardMarkup:
    # nums_for_choose = [InlineKeyboardButton(text=str(x), callback_data=str(x)) for x in
    #                    range(1, key_list.__len__() + 1)]
    # rows = [
    #     nums_for_choose,
    # ]
    rows = []
    counter = 1
    for elem in key_list:
        rows.append([
            InlineKeyboardButton (
                text=elem,
                callback_data=str(counter)
            )
        ])
        counter += 1
    if can_go_left and can_go_right:
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
    if can_go_back:
        rows.append(
            [InlineKeyboardButton(
                text='В предыдущую директорию',
                callback_data='prev_dir'
            )])
    # TODO убрать?
    rows.append(
        [
            InlineKeyboardButton(
                text='Показать все презентации',
                callback_data='show_all_pres'
            )
        ])
    if file_type == 'font':
        rows.append(
            [InlineKeyboardButton(
                text='Забрать все шрифты',
                callback_data='get_fonts_from_all_pres'
            )])
    rows.append(
        [
            InlineKeyboardButton(
                text='Вернуться к выбору материалов',
                callback_data='menu_choose'
            )
        ]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


# Only for 'font'
async def choose_category_in_deadend_callback_for_fonts(can_go_back: bool) -> InlineKeyboardMarkup:
    rows = []
    rows.append(
        [InlineKeyboardButton(
            text='Скачать',
            callback_data='get_fonts_from_all_pres'
        )])
    if can_go_back:
        rows.append(
            [InlineKeyboardButton(
                text='В предыдущую директорию',
                callback_data='prev_dir'
            )])
    rows.append(
        [
            InlineKeyboardButton(
                text='В главное меню',
                callback_data='menu_choose'
            )
        ]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


# Only for 'template'
async def choose_category_in_deadend_callback_for_templates(can_go_back: bool) -> InlineKeyboardMarkup:
    rows = []
    rows.append(
        [
            InlineKeyboardButton(
                text='В главное меню',
                callback_data='menu_choose'
            )
        ]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def no_font() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text='Вернуться к выбору материалов',
            callback_data='menu_choose'
        )]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def go_to_main_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text='Отмена',
            callback_data='main_menu'
        )]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def error_in_send_file() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text='Вернуться к выбору материалов',
            callback_data='menu_choose'
        )]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def tags_buttons(tags: list) -> InlineKeyboardMarkup:
    rows = []
    counter = 1
    for tag in tags:
        rows.append([
            InlineKeyboardButton(
                text=tag['name'],
                callback_data=str(counter)
            )
        ])
        counter += 1
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def choose_category_template(key_list: list, can_go_left: bool, can_go_right: bool,
                                   can_go_back: bool, file_type: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for elem in key_list:
        kb.add(types.KeyboardButton(text=elem))
    kb.button(text="Показать все презентации")
    if file_type == 'font':
        kb.button(text='Забрать все шрифты')
    if can_go_right:
        kb.button(text="Далее")
    if can_go_left:
        kb.button(text="Назад")
    if can_go_back:
        kb.button(text="В предыдущую директорию")
    kb.button(text="В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


async def admin_choose_category_template(key_list: list, can_go_left: bool, can_go_right: bool,
                                         can_go_back: bool, action: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for elem in key_list:
        kb.add(types.KeyboardButton(text=elem))
    kb.adjust(3)
    print('admin_choose')
    if action == 'delete':
        kb.button(text="Показать все презентации")
        kb.adjust(1)
    if action == 'add':
        kb.button(text="Добавить сюда")
        kb.adjust(1)
    if can_go_right:
        kb.button(text="Далее")
    if can_go_left:
        kb.button(text="Назад")
    kb.adjust(2)
    if can_go_back:
        kb.button(text="В предыдущую директорию")
    kb.button(text="В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


async def admin_choose_category_template_query(key_list: list, can_go_left: bool,
                                               can_go_right: bool, can_go_back: bool,
                                               action: str) -> InlineKeyboardMarkup:
    nums_for_choose = [InlineKeyboardButton(text=str(x), callback_data=str(x)) for x in
                       range(1, key_list.__len__() + 1)]
    rows = [
        nums_for_choose,
    ]
    if can_go_left and can_go_right:
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
    if can_go_back:
        rows.append(
            [InlineKeyboardButton(
                text='В предыдущую директорию',
                callback_data='prev_dir'
            )])
    if action == 'add':
        rows.append(
            [
                InlineKeyboardButton(
                    text='Добавить сюда',
                    callback_data='add_here'
                )
            ]
        )
    if action == 'delete':
        rows.append(
            [InlineKeyboardButton(
                text='Показать все презентации',
                callback_data='show_all_pres_for_delete'
            )])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def admin_panel() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Добавить материал")
    kb.button(text="Удалить материал")
    kb.button(text="В главное меню")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_panel_query() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text="Добавить материал",
                callback_data="admin_add"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить материал",
                callback_data="admin_delete"
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить нового администратора",
                callback_data="new_admin_add"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить администратора",
                callback_data="old_admin_delete"
            )
        ],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
