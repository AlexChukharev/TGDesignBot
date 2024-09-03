from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rows_for_main_menu():
    rows = [
        [InlineKeyboardButton(
            text='Не получается сделать слайд, помоги',
            callback_data='search_by_tags'
        )],
        [InlineKeyboardButton(
            text='Найти шаблон для презентаций',
            callback_data='pres_templates'
        )],
        [InlineKeyboardButton(
            text='Скачать корпоративные шрифты',
            callback_data='fonts'
        )],
        [InlineKeyboardButton(
            text='Нужен дизайнер — поставить задачу',
            callback_data='designer'
        )],
        [InlineKeyboardButton(
            text='Хочу дать обратную связь',
            callback_data='bot_feedback'
        )]
    ]
    return rows


def row_back_to_main_menu():
    return [main_menu_inline_button()]


def main_menu_inline_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='В главное меню',
        callback_data='start'
    )


def prev_dir_inline_button()-> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Назад',
        callback_data='prev_dir'
    )

def prev_inline_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
                text='Предыдущие варианты',
                callback_data='prev'
            )


def next_inline_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text='Еще варианты',
        callback_data='next'
    )


async def main_menu_buttons_from_query() -> InlineKeyboardMarkup:
    rows = rows_for_main_menu()
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def get_fonts_buttons() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text='Скачать необходимые шрифты',
                callback_data='get_fonts'
            )
        ],
        row_back_to_main_menu()
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def how_to_install_fonts_buttons():
    rows = [
        [
            InlineKeyboardButton(
                text='Как установить шрифты?',
                callback_data='install_fonts_help'
            )
        ],
        row_back_to_main_menu()
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def choose_template_text_inner(folder: str) -> str:
    text = f"У нас есть несколько шаблонов для подразделения {folder}\nКакой тебе нужен?\n \n"
    return text


async def choose_template_text_root(type_file: str) -> str:
    if type_file == 'template':
        return f"Для какого подразделения нужен шаблон?\n"
    if type_file == 'font':
        return f"У нас очень много шрифтов — тебе для какого подразделения нужны?\n"
    if type_file == 'search_by_tags':
        return f"Я подскажу варианты, как можно оформить твой контент!\n" \
           f"Расскажи, какой слайд нужен?\n"
           # f"Но для начала, подскажи, в каком шаблоне ты делаешь презентацию?\n"


# async def choose_one_file(key_list: list, paths_list: list) -> str:
#     text = "Выберите один из файлов для установки \n \n"
#     text += await key_list_with_paths(key_list, paths_list)
#     return text


# async def key_list_with_paths(key_list: list, path_list: list) -> str:
#     text = ""
#     counter = 1
#     for elem_num in range(len(key_list)):
#         text += f"{counter}. {key_list[elem_num]} \n"
#         text += f"Путь: {path_list[elem_num]} \n \n"
#         counter += 1
#     return text


async def choose_category_callback(key_list: list, can_go_left: bool, can_go_right: bool,
                                   can_go_back: bool, file_type: str) -> InlineKeyboardMarkup:
    rows = []
    counter = 1
    for elem in key_list:
        rows.append([
            InlineKeyboardButton(
                text=elem,
                callback_data=str(counter)
            )
        ])
        counter += 1

    if can_go_left and can_go_right:
        rows.append([
            prev_inline_button(),
            next_inline_button()
        ])
    elif can_go_right:
        rows.append([
            next_inline_button()
        ])
    elif can_go_left:
        rows.append([
            prev_inline_button()
        ])

    if file_type == 'font':
        rows.append(
            [InlineKeyboardButton(
                text='Забрать сразу все',
                callback_data='get_fonts_from_all_pres'
            )])

    if can_go_back:
        rows.append(
            [prev_dir_inline_button(), main_menu_inline_button()]
        )
    else:
        rows.append(
            row_back_to_main_menu()
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
            [prev_dir_inline_button(), main_menu_inline_button()]
        )
    else:
        rows.append(
            row_back_to_main_menu()
        )
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def go_back_to_main_menu() -> InlineKeyboardMarkup:
    rows = [row_back_to_main_menu()]
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
    rows.append(row_back_to_main_menu())
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


# async def choose_file_kb_query(key_list: list, can_go_left: bool, can_go_right: bool) -> InlineKeyboardMarkup:
#     rows = await choose_file_kb_query_handler(key_list, can_go_left, can_go_right)
#     rows.append(row_back_to_main_menu())
#     markup = InlineKeyboardMarkup(inline_keyboard=rows)
#     return markup


# async def choose_file_kb_query_handler(key_list: list, can_go_left: bool, can_go_right: bool) -> list:
#     nums_for_choose = [
#         InlineKeyboardButton(
#             text=str(x),
#             callback_data=str(x)
#         ) for x in range(1, key_list.__len__() + 1)
#     ]
#     rows = [nums_for_choose]
#
#     if can_go_left and can_go_right:
#         rows.append([
#             prev_inline_button(),
#             next_inline_button()
#         ])
#     elif can_go_right:
#         rows.append([
#             next_inline_button()
#         ])
#     elif can_go_left:
#         rows.append([
#             prev_inline_button()
#         ])
#
#     return rows
