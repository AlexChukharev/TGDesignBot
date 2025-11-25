from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

from messages.messages_store import store as messages_store


def rows_for_main_menu(lang: str):
    rows = [
        [InlineKeyboardButton(
            text=messages_store.get("buttons.search_by_tags", lang),
            callback_data='search_by_tags'
        )],
        [InlineKeyboardButton(
            text=messages_store.get("buttons.pres_templates", lang),
            callback_data='pres_templates'
        )],
        [InlineKeyboardButton(
            text=messages_store.get("buttons.fonts", lang),
            callback_data='fonts'
        )],
        [InlineKeyboardButton(
            text=messages_store.get("buttons.extra_assets", lang),
            callback_data='extra_assets'
        )],
        [InlineKeyboardButton(
            text=messages_store.get("buttons.about_company", lang),
            callback_data='about_company'
        )],
        [
            InlineKeyboardButton(
            text=messages_store.get("buttons.designer", lang),
            callback_data='designer'),
            InlineKeyboardButton(
            text='🌎 Wiki Int',
            callback_data='english_assets')
        ],
        [InlineKeyboardButton(
            text=messages_store.get("buttons.bot_faq", lang),
            callback_data='bot_faq'
        )]
    ]
    return rows


def language_rows():
    rows = [
    [
        InlineKeyboardButton(
            text='🇷🇺',
            callback_data='set_lang_ru'
        ),
        InlineKeyboardButton(
            text='🇬🇧',
            callback_data='set_lang_en'
        )
    ]
    ]
    return rows


def intro_language_rows():
    rows = [
    [
        InlineKeyboardButton(
            text='🇷🇺',
            callback_data='intro_set_lang_ru'
        ),
        InlineKeyboardButton(
            text='🇬🇧',
            callback_data='intro_set_lang_en'
        )
    ]
    ]
    return rows


def feedback_buttons_row():
    rows = [
        InlineKeyboardButton(
            text='😍',
            callback_data='feedback_great'
        ),
        InlineKeyboardButton(
            text='😔',
            callback_data='feedback_bad'
        )
    ]
    return rows


async def go_back_to_main_menu_with_feedback(lang: str) -> InlineKeyboardMarkup:
    rows = [feedback_buttons_row(), row_back_to_main_menu(lang)]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def freshness_button(lang: str) -> InlineKeyboardButton:
    callback_data_text = 'freshness_feedback'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    return InlineKeyboardButton(
        text=msg,
        callback_data=callback_data_text
    )


async def go_back_to_main_menu_with_feedback_and_freshness(lang: str) -> InlineKeyboardMarkup:
    rows = [
        feedback_buttons_row(), 
        [freshness_button(lang)],
        row_back_to_main_menu(lang)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def row_back_to_main_menu(lang: str):
    return [main_menu_inline_button(lang)]


def main_menu_inline_button(lang: str) -> InlineKeyboardButton:
    callback_data_text = 'main_menu'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    return InlineKeyboardButton(
        text=msg,
        callback_data=callback_data_text
    )


def prev_dir_inline_button(lang: str) -> InlineKeyboardButton:
    callback_data_text = 'prev_dir'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    return InlineKeyboardButton(
        text=msg,
        callback_data=callback_data_text
    )

def prev_inline_button(lang: str) -> InlineKeyboardButton:
    callback_data_text = 'prev'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    return InlineKeyboardButton(
                text=msg,
                callback_data=callback_data_text
            )


def next_inline_button(lang: str) -> InlineKeyboardButton:
    callback_data_text = 'next'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    return InlineKeyboardButton(
        text=msg,
        callback_data=callback_data_text
    )


async def main_menu_buttons_from_query(lang: str) -> InlineKeyboardMarkup:
    rows = rows_for_main_menu(lang)
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def language_buttons_from_query() -> InlineKeyboardMarkup:
    rows = language_rows()
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def intro_language_buttons_from_query() -> InlineKeyboardMarkup:
    rows = intro_language_rows()
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def get_fonts_buttons(lang: str) -> InlineKeyboardMarkup:
    callback_data_text = 'get_fonts'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    rows = [
        [
            InlineKeyboardButton(
                text=msg,
                callback_data=callback_data_text
            )
        ],
        row_back_to_main_menu(lang)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def get_fonts_buttons_with_feedback(lang: str) -> InlineKeyboardMarkup:
    callback_data_text = 'get_fonts'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    rows = [
        feedback_buttons_row(),
        [
            InlineKeyboardButton(
                text=msg,
                callback_data=callback_data_text
            )
        ],
        row_back_to_main_menu(lang)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def how_to_install_fonts_buttons(lang: str):
    callback_data_text = 'install_fonts_help'
    msg = messages_store.get(f"buttons.{callback_data_text}", lang)
    rows = [
        [
            InlineKeyboardButton(
                text=msg,
                callback_data=callback_data_text
            )
        ],
        row_back_to_main_menu(lang)
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def choose_text_inner(folder, lang: str) -> str:
    return messages_store.get("menu.choose_text_inner", lang, folder=folder)


async def choose_text_root(type_file, lang: str) -> str:
    if type_file == 'template':
        return messages_store.get("menu.choose_text_root_template", lang)
    if type_file == 'font':
        return messages_store.get("menu.choose_text_root_font", lang)
    if type_file == 'search_by_tags':
        return messages_store.get("menu.choose_text_root_search_by_tags", lang)
    if type_file == 'about_company':
        return messages_store.get("menu.choose_text_root_about_company", lang)
    if type_file == 'extra_assets':
        return messages_store.get("menu.choose_text_root_extra_assets", lang)


async def choose_category_callback(key_list: list, can_go_left: bool, can_go_right: bool,
                                   can_go_back: bool, file_type, lang: str) -> InlineKeyboardMarkup:
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
            prev_inline_button(lang),
            next_inline_button(lang)
        ])
    elif can_go_right:
        rows.append([
            next_inline_button(lang)
        ])
    elif can_go_left:
        rows.append([
            prev_inline_button(lang)
        ])

    if file_type == 'font':
        rows.append(
            [InlineKeyboardButton(
                text=messages_store.get("buttons.get_fonts_from_all_pres", lang),
                callback_data='get_fonts_from_all_pres'
            )])

    if can_go_back:
        rows.append(
            [prev_dir_inline_button(lang), main_menu_inline_button(lang)]
        )
    else:
        rows.append(
            row_back_to_main_menu(lang)
        )

    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def go_back_to_main_menu(lang: str) -> InlineKeyboardMarkup:
    rows = [row_back_to_main_menu(lang)]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def go_back_in_tags_inline_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=messages_store.get("buttons.go_back_in_tags_inline_button", lang),
        callback_data='0'
    )


async def tags_buttons(tags: list, can_go_back: bool, need_another_button: bool, lang: str) -> InlineKeyboardMarkup:
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
    if need_another_button:
        rows.append([
            InlineKeyboardButton(
                text=messages_store.get("buttons.another_idea", lang),
                callback_data='another_idea'
            )
        ])
    if (can_go_back):
        rows.append(
            [go_back_in_tags_inline_button(lang), main_menu_inline_button(lang)]
        )
    else:
        rows.append(row_back_to_main_menu(lang))
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


def search_by_tags_from_start_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=messages_store.get("buttons.ideas_from_start", lang),
        callback_data='ideas_from_start'
    )


async def ideas_final_buttons(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [search_by_tags_from_start_button(lang)], 
        row_back_to_main_menu(lang)
        ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup


async def ideas_final_buttons_with_feedback(lang: str) -> InlineKeyboardMarkup:
    rows = [
        feedback_buttons_row(), 
        [search_by_tags_from_start_button(lang)], 
        row_back_to_main_menu(lang)
        ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
