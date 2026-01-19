import logging 
import json

from aiogram.enums import ParseMode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from messages.messages_store import get_random_from_prefix
from messages.messages_store import store as messages_store
from utility.logging_actions import log_action_with_username, log_sending
from utility.tg_utility import error_final, language_check, try_to_delete_message, \
    download_with_link_query, send_file_from_local_for_query, error_text

from DBHandler import (
    get_fonts_by_template_id,
    delete_template,
    get_template_id_by_name
)

from YandexDisk.YaDiskInfo import TemplateInfo
from YandexDisk import get_download_link, get_file_size

from ...keyboards import go_back_to_main_menu, how_to_install_fonts_buttons


router = Router()
logger = logging.getLogger(__name__)


class WalkerState(StatesGroup):
    # In the state we store child_list, indx_list_start\end, can_go_back
    choose_button = State()
    choose_category = State()
    choose_file = State()


@router.callback_query(WalkerState.choose_file, F.data == "get_fonts")
async def get_fonts(callback_query: CallbackQuery, state: FSMContext):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    user_info = await state.get_data()
    template_id = user_info["file_id"]
    list_fonts = get_fonts_by_template_id(template_id)

    if len(list_fonts) == 0:
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return

    try:
        await callback_query.message.edit_text(
            text=get_random_from_prefix("waiting", lang)
        )
    except Exception as e:
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        logger.info(e)
        return
    
    try:
        path = list_fonts[0][1] + '/' + list_fonts[0][3]
        log_sending(logger, path)
        link = get_download_link(path)
        await download_with_link_query(callback_query, link, 'fonts.zip', lang)

        reply_markup = await how_to_install_fonts_buttons(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=get_random_from_prefix("done", lang),
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.info(e)


@router.callback_query(WalkerState.choose_file, F.data == "install_fonts_help")
@router.callback_query(WalkerState.choose_button, F.data == "install_fonts_help")
async def send_info(callback_query: CallbackQuery):
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = await language_check(callback_query)
    if not lang:
        return

    try:
        await callback_query.message.edit_text(
            text=messages_store.get("sending.instruction", lang)
        )
    except Exception as e:
        logger.info(e)
    if lang == 'ru':
        path = './Data/Appdata/Инструкция по установке шрифтов.pdf'
        log_sending(logger, path)
        await send_file_from_local_for_query(callback_query, path, 'Инструкция по установке шрифтов.pdf')
    else:
        path = './Data/Appdata/How to install fonts.pdf'
        log_sending(logger, path)
        await send_file_from_local_for_query(callback_query, path, 'How to install fonts.pdf')
    reply_markup = await go_back_to_main_menu(lang)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=messages_store.get("sending.instruction_done", lang),
        reply_markup=reply_markup
    )
