import json
from telegram.constants import ParseMode

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from TelegramHandler.keyboards import go_back_to_main_menu, back_to_start

router = Router()


# @router.message(F.text.lower() == "стоп, а что ты умеешь?")
@router.message(Command("actions"))
async def cmd_help(message: Message):
    await message.answer(
        "Я – бот отдела визуальных коммуникаций екома и райдтеха. Я умею находить нужные тебе материалы и помогать в создании слайдов – потыкай кнопочки, чтобы узнать подробнее)"
    )


@router.message(Command("help"))
@router.message(F.text.lower() == "хочу дать обратную связь")
async def cmd_feedback(message: Message):
    await message.reply(
        f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
    )


@router.callback_query(F.data == "bot_feedback")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await back_to_start()
    # await callback_query.message.edit_text(
    #     f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
    # )
    text = f"По любым проблемам с ботом или материалами пиши {json.load(open('./config.json'))['owner']}"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "designer")
async def cmd_feedback(callback_query: CallbackQuery):
    reply_markup = await go_back_to_main_menu()
    link = "https://forms.yandex-team.ru/surveys/VISCOMMS/"
    text = f"Заполни форму по <a href='{link}'>ссылке</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
#     https://forms.yandex-team.ru/surveys/VISCOMMS/
