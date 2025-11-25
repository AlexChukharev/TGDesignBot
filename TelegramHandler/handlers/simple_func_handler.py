import json
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from TelegramHandler.keyboards import go_back_to_main_menu

from messages.languages import get_user_lang
from utility.logging_actions import log_action_with_username, log_unauthorized
from utility.tg_utility import choose_language, no_access_text
from utility.checkers import is_user


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("help"))
async def cmd_feedback(message: Message, state: FSMContext):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    has_access = await is_user(message.from_user.id, message.from_user.username)
    if not has_access:
        log_unauthorized(logger, message.from_user.username, message.from_user.id)
        await message.answer(
        text=no_access_text()
        )
        return
    
    await state.clear()
    reply_markup = await go_back_to_main_menu()
    text = f"По любым проблемам, связанным с ботом или материалами, обязательно пиши {json.load(open('./CONFIG/config.json'))['owner']}"
    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.message(Command("news"))
async def cmd_feedback(message: Message, state: FSMContext):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    has_access = await is_user(message.from_user.id, message.from_user.username)
    if not has_access:
        log_unauthorized(logger, message.from_user.username, message.from_user.id)
        await message.answer(
        text=no_access_text()
        )
        return
    
    await state.clear()
    reply_markup = await go_back_to_main_menu()
    link = "https://t.me/+TWPGaiWjuOXDlAPm"
    text = f"<a href='{link}'>На канале</a> делимся самыми интересными апдейтами: \nновости бота, изменения в материалах и немного закулисья"
    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "bot_faq")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = get_user_lang(callback_query.from_user.id)
    if not lang:
        await choose_language(callback_query)
        return

    reply_markup = await go_back_to_main_menu()
    text = f"По любым вопросам, связанным с ботом или материалами, пиши {json.load(open('./CONFIG/config.json'))['owner']}\n\n"\
        f"Have any questions or suggestions about the bot or the materials? \nPlease, drop a message to {json.load(open('./CONFIG/config.json'))['owner']}"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    


@router.callback_query(F.data == "designer")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    reply_markup = await go_back_to_main_menu()
    link = "https://wiki.yandex-team.ru/viscomms/"
    text = f"Держи, вот <a href='{link}'>ссылка на вики</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "english_assets")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    reply_markup = await go_back_to_main_menu()
    link = "https://wiki.yandex-team.ru/viscomms/yango-group-presentations/"
    text = f"Here you go: <a href='{link}'>the wiki with all relevant assets</a>"
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
