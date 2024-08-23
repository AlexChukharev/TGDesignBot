import json

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

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
