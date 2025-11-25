import json
import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from TelegramHandler.keyboards.buttons import get_fonts_buttons, go_back_to_main_menu, ideas_final_buttons
from messages.languages import get_user_lang
from utility.logging_actions import log_action_with_username
from utility.tg_utility import choose_language, error_final, error_text, get_list_of_files, try_to_delete_message

from messages.messages_store import store as messages_store

router = Router()
logger = logging.getLogger(__name__)


def thanks_for_feedback_text(type_file: str, score: str, lang: str) -> str:
    if score == "feedback_bad":
        owner = json.load(open('./CONFIG/config.json'))['owner']
        text = messages_store.get("feedback.thanks_for_bad", lang, owner=owner)
    else:
        text = reply_text = messages_store.get("feedback.thanks_for_good", lang)
            
    if type_file != "extra_assets" and type_file != "search_by_tags":
        text += "\n" + messages_store.get("feedback.fonts_reminder", lang)

    return text


@router.callback_query(F.data == "feedback_great")
@router.callback_query(F.data == "feedback_bad")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes feedback buttons and saves to feedback.csv
    """
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)

    lang = get_user_lang(callback_query.from_user.id)
    if not lang:
        await choose_language(callback_query)
        return

    files_list = await get_list_of_files(state)
    user_info = await state.get_data()
    type_file = user_info['type_file']
    if not files_list:
        text = await error_text(lang)
        await error_final(callback_query, text, lang)
        return
    file_name = files_list[0][2]
    file_path = files_list[0][1]

    feedback_text = str(file_path) + '/' + str(file_name) + ", " + callback_query.data + ", " + \
            callback_query.from_user.username + ", " + datetime.today().strftime('%Y-%m-%d')

    reply_text = thanks_for_feedback_text(type_file, callback_query.data, lang)
    if type_file == "extra_assets":
        reply_markup = await go_back_to_main_menu(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
    elif type_file == "search_by_tags":
        feedback_text += ", " + user_info['tags']['tag']
        reply_markup = await ideas_final_buttons(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
    else:
        reply_markup = await get_fonts_buttons(lang)
        await try_to_delete_message(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=reply_text,
            reply_markup=reply_markup
        )
    logger.info(feedback_text)


@router.callback_query(F.data == "freshness_feedback")
async def prev_template_find(callback_query: CallbackQuery, state: FSMContext):
    """
        Processes freshness feedback button. Used for Logo files
    """
    log_action_with_username(logger, callback_query.data, callback_query.from_user.username, callback_query.from_user.id)
    
    lang = get_user_lang(callback_query.from_user.id)
    if not lang:
        await choose_language(callback_query)
        return

    reply_markup = await go_back_to_main_menu(lang)
    owner = json.load(open('./CONFIG/config.json'))['owner']
    reply_text = messages_store.get("feedback.freshness_feedback", lang, owner=owner)
    await try_to_delete_message(callback_query)
    await callback_query.bot.send_message(
        chat_id=callback_query.from_user.id,
        text=reply_text,
        reply_markup=reply_markup
    )
