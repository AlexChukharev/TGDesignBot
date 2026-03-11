import logging
from aiogram import Router
from aiogram.types import Message
from messages.languages import get_user_lang
from telegram import CallbackQuery

from TelegramHandler.keyboards.buttons import go_back_to_main_menu
from utility.logging_actions import log_action_with_username
from utility.tg_utility import choose_language, try_to_delete_message
from utility.logging_actions import log_action_with_username, log_unauthorized
from utility.tg_utility import no_access_text
from utility.checkers import is_user

from messages.messages_store import store as messages_store

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def no_handled_message(message: Message):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    has_access = await is_user(message.from_user.id, message.from_user.username)
    if not has_access:
        log_unauthorized(logger, message.from_user.username, message.from_user.id)
        await message.answer(
        text=no_access_text("ru")
        )
        return


@router.callback_query()
async def no_handled_query(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = get_user_lang(callback_query.from_user.id)
    if not lang:
        await choose_language(callback_query)
        return
    
    reply_markup = await go_back_to_main_menu(lang)
    reply_text = messages_store.get("no_handled.query", lang)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        reply_markup=reply_markup
    )