import json

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from TelegramHandler.keyboards import go_back_to_main_menu

router = Router()


@router.message(Command("help"))
async def cmd_feedback(message: Message):
    text = f"Привет! Если пропали кнопки, выбирай команду /start\n\n" \
        f"По любым проблемам с ботом или материалами обязательно пиши {json.load(open('./config.json'))['owner']}"
    await message.reply(
        text=text,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "bot_feedback")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await go_back_to_main_menu()
    text = f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    


@router.callback_query(F.data == "designer")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await go_back_to_main_menu()
    link = "https://wiki.yandex-team.ru/viscomms/"
    text = f"Держи, вот <a href='{link}'>ссылка на вики</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
