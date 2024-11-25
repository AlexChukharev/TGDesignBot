import json
from telegram.constants import ParseMode

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from TelegramHandler.keyboards import go_back_to_main_menu

router = Router()


@router.message(Command("about"))
async def cmd_help(message: Message):
    # await message.answer(
    #     f'Привет, {message.from_user.first_name}!\nЯ Viscomms, бот команды визуальных коммуникаций.'\
    #     f'Обращайся ко мне, если нужно найти материалы для презентаций или помочь с дизайном\n\n'\
    #     f'Я только начал свою работу и стремлюсь быть максимально полезным и удобным. Буду рад обратной связи!'
    # )
    await message.answer(
        text=f'Привет, {message.from_user.first_name}!\nЯ &mdash; бот-помощник команды визуальных коммуникаций. '\
        f'Могу найти материалы для презентаций, подобрать подходящую визуализацию или помочь поставить задачу команде дизайнеров\n\n'\
        f'Я только начинаю свой путь и стремлюсь развиваться, поэтому буду рад твоей обратной связи и идеям для улучшения!',
        parse_mode=ParseMode.HTML
    )


@router.message(Command("help"))
@router.message(F.text.lower() == "хочу дать обратную связь")
async def cmd_feedback(message: Message):
    link = 'https://t.me/+8i1uLItQYgNhZjZi'
    await message.reply(
        # f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
        text=f"По любым проблемам с ботом или материалами обязательно пиши <a href='{link}'>в чат</a>",
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "bot_feedback")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await go_back_to_main_menu()
    link = 'https://t.me/+8i1uLItQYgNhZjZi'
    # text = f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
    text = f"По любым проблемам с ботом или материалами обязательно пиши <a href='{link}'>в чат</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    


@router.callback_query(F.data == "designer")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await go_back_to_main_menu()
    # link = "https://forms.yandex-team.ru/surveys/VISCOMMS/"
    link = "https://wiki.yandex-team.ru/viscomms/"
    text = f"Держи, вот <a href='{link}'>ссылка на вики</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
