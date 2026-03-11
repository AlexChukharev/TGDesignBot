import json
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from CONFIG.config import CONFIG
from TelegramHandler.keyboards import go_back_to_main_menu

from utility.logging_actions import log_action_with_username
from utility.tg_utility import access_and_language_check, language_check

from messages.messages_store import store as messages_store

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("help"))
async def cmd_feedback(message: Message, state: FSMContext):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    lang = await access_and_language_check(message)
    if not lang:
        return

    await state.clear()
    reply_markup = await go_back_to_main_menu(lang)
    text = messages_store.get("simples.help", lang, owner=CONFIG['owner'])
    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.message(Command("news"))
async def cmd_feedback(message: Message, state: FSMContext):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    lang = await access_and_language_check(message)
    if not lang:
        return
    
    await state.clear()
    reply_markup = await go_back_to_main_menu(lang)
    text = messages_store.get("simples.news", lang)
    await message.answer(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "bot_faq")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    reply_markup = await go_back_to_main_menu(lang)
    text = messages_store.get("simples.bot_faq", lang, owner=CONFIG['owner'])
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    


@router.callback_query(F.data == "designer")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    reply_markup = await go_back_to_main_menu(lang)
    text = messages_store.get("simples.designer", lang)
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "english_assets")
async def cmd_feedback(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    reply_markup = await go_back_to_main_menu(lang)
    text = messages_store.get("simples.english_assets", lang)
    await callback_query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
