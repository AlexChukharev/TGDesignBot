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
    return [InlineKeyboardButton(
        text='В главное меню',
        callback_data='start'
    )]


async def main_menu_buttons_from_query() -> InlineKeyboardMarkup:
    rows = rows_for_main_menu()
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def main_menu_kb_query():
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


async def choose_template_text_inner(folder: str, key_list: list) -> str:
    text = f"У нас есть несколько шаблонов для подразделения {folder}\nКакой тебе нужен?\n \n"
    return text


async def choose_template_text_root_for_templates(key_list: list) -> str:
    text = f"Для какого подразделения нужен шаблон?\n"
    return text


async def choose_template_text_root_for_fonts(key_list: list) -> str:
    text = f"У нас очень много шрифтов, какие тебе нужны?\n"
    return text


async def choose_template_text_root_for_tags(key_list: list) -> str:
    text = f"Я подскажу варианты, как можно оформить твой контент!\n" \
           f"Но для начала, подскажи, в каком шаблоне ты делаешь презентацию?\n"
    return text


async def choose_one_file(key_list: list, paths_list: list) -> str:
    text = "Выберите один из файлов для установки \n \n"
    text += await key_list_with_paths(key_list, paths_list)
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
                text='Назад',
                callback_data='prev_dir'
            )])
    if file_type == 'font':
        rows.append(
            [InlineKeyboardButton(
                text='Забрать все шрифты',
                callback_data='get_fonts_from_all_pres'
            )])
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
            [InlineKeyboardButton(
                text='Назад',
                callback_data='prev_dir'
            )])
    rows.append(
        row_back_to_main_menu()
    )
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def go_back_to_main_menu() -> InlineKeyboardMarkup:
    rows = [
        row_back_to_main_menu()
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
