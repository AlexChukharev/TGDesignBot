import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums import ParseMode

from messages.languages import get_user_lang
from utility.checkers import is_user
from utility.logging_actions import log_action_with_username, log_unauthorized
from utility.tg_utility import access_and_language_check, choose_language, no_access_text, error_no_access

from ..keyboards.buttons import intro_language_buttons_from_query, main_menu_buttons_from_query

from messages.messages_store import store as messages_store


router = Router()
logger = logging.getLogger(__name__)


class UserStates(StatesGroup):
    in_main_menu = State()
    in_choose_category = State()
    find_images = State()
    find_templates = State()
    find_slides_about_company = State()
    find_fonts = State()
    find_ready_structs = State()


@router.message(Command("start"))
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
    reply_markup = await intro_language_buttons_from_query()

    await message.answer_photo(
        FSInputFile(path="./Data/Appdata/Images/start.png")
    )

    msg_text = messages_store.get("intro.lang", "ru")
    msg_text += messages_store.get("intro.lang", "en")
    await message.answer(
        text=msg_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "main_menu")
async def main_start_handler(callback_query: CallbackQuery, state: FSMContext):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    has_access = await is_user(callback_query.from_user.id, callback_query.from_user.username)
    if not has_access:
        log_unauthorized(logger, callback_query.from_user.username, callback_query.from_user.id)
        await error_no_access(callback_query)
        return
    
    lang = get_user_lang(callback_query.from_user.id)
    if not lang:
        await choose_language(callback_query)
        return

    await state.clear()
    reply_markup = await main_menu_buttons_from_query(lang)
    await callback_query.message.edit_text(
        messages_store.get("menu.main", lang),
        reply_markup=reply_markup
    )


@router.message(Command(commands=["menu"]))
@router.message(F.text.lower() == "в главное меню")
async def cmd_cancel_handler(message: Message, state: FSMContext):
    print("HERE in menu command")
    log_action_with_username(logger, message.text, message.from_user.username, message.from_user.id)

    lang = access_and_language_check(message)
    if not lang:
        return
    
    await state.clear()
    reply_markup = await main_menu_buttons_from_query(lang)
    await message.answer(
        text="Чем могу помочь?",
        reply_markup=reply_markup
    )
