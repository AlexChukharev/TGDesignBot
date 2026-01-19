import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums import ParseMode


from messages.languages import set_user_lang
from utility.checkers import is_user
from utility.logging_actions import log_action_with_username, log_unauthorized
from utility.tg_utility import no_access_text, error_no_access, try_to_delete_message


from ..keyboards.buttons import language_buttons_from_query, main_menu_buttons_from_query

from messages.messages_store import store


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("intro_set_lang_"))
async def intro_set_language_handler(callback_query: CallbackQuery, state: FSMContext):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    has_access = await is_user(callback_query.from_user.id, callback_query.from_user.username)
    if not has_access:
        log_unauthorized(logger, callback_query.from_user.username, callback_query.from_user.id)
        await error_no_access(callback_query)
        return
    
    lang = callback_query.data.split("_")[-1]
    set_user_lang(callback_query.from_user.id, lang)

    await state.clear()
    reply_markup = await main_menu_buttons_from_query(lang)

    await try_to_delete_message(callback_query)

    msg_text = store.get("intro.intro", lang, name=callback_query.from_user.first_name)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=msg_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    msg_text = store.get("menu.main", lang)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=msg_text,
        reply_markup=reply_markup
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def intro_set_language_handler(callback_query: CallbackQuery, state: FSMContext):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    has_access = await is_user(callback_query.from_user.id, callback_query.from_user.username)
    if not has_access:
        log_unauthorized(logger, callback_query.from_user.username, callback_query.from_user.id)
        await error_no_access(callback_query)
        return
    
    lang = callback_query.data.split("_")[-1]
    set_user_lang(callback_query.from_user.id, lang)

    await state.clear()
    reply_markup = await main_menu_buttons_from_query(lang)


    await try_to_delete_message(callback_query)
    
    msg_text = store.get("menu.main", lang)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=msg_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.message(Command("set_language"))
async def cmd_start_handler(message: Message, state: FSMContext):
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    has_access = await is_user(message.from_user.id, message.from_user.username)
    if not has_access:
        log_unauthorized(logger, message.from_user.username, message.from_user.id)
        await message.answer(
        text=no_access_text("ru")
        )
        return
    
    await state.clear()
    reply_markup = await language_buttons_from_query()

    msg_text = store.get("intro.lang", "ru")
    msg_text += store.get("intro.lang", "en")
    await message.answer(
        text=msg_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )