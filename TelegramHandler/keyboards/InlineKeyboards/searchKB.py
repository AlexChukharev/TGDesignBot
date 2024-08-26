from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def build_choose_kb() -> InlineKeyboardMarkup:
    search_by_tags = InlineKeyboardButton(
        text='Не получается сделать слайд, помоги',
        callback_data='search_by_tags'
    )
    templates = InlineKeyboardButton(
        text='Шаблон презентаций',
        callback_data='pres_templates'
    )
    # slides = InlineKeyboardButton(
    #     text='Готовые слайды о компании',
    #     callback_data='slides'
    # )
    fonts = InlineKeyboardButton(
        text='Корпоративные шрифты',
        callback_data='fonts'
    )
    rows = [
        [search_by_tags],
        [templates],
        # [slides],
        [fonts]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
