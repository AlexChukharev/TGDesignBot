from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# DEPRECATED
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
    deprecated = InlineKeyboardButton(
        text='DEPRECATED ITEM',
        callback_data='deprecated'
    )
    rows = [
        # [search_by_tags],
        # [templates],
        # # [slides],
        # [fonts]
        [deprecated]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
